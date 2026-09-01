# LearningHouse — Modernization and Enablement Plan

**Repository:** `LearningHouseService/learninghouse`
**Goal:** Bring the existing service up to current engineering standards and make it capable of
hosting domain-specific brains — starting with PV forecasting via
[`pvlearn`](https://github.com/LearningHouseService/pvlearn) — and of shipping as a Home
Assistant add-on.

**Scope boundary:** This plan stops before the pvlearn *integration*. Scheduled weather retrieval,
an event bus, horizon predictions and the API changes those require are deliberately out of scope
and get their own plan once this one is delivered. What this plan does is remove every obstacle
that would make those changes expensive or unsafe.

---

## 1. Where the project stands today

Measured against the current `main` (3,735 lines of Python across `core/learninghouse`, Angular 21
UI, single CI workflow).

**There are no tests.** `core/tests/` contains nothing but an empty `__init__.py`, and
`.github/workflows/build_project.yml` has no test, lint or type-check step. The pipeline builds the
UI, builds the wheel, and pushes a Docker image. Every phase below changes behaviour that nothing
currently verifies.

**Packaging is a generation behind.** `setup.py` + `setup.cfg` + `versioneer.py` +
`requirements.txt`, where `pvlearn` already uses `pyproject.toml` with `setuptools-scm`. No Ruff, no
Pyright, no coverage gate.

**State is process-global in several modules.** `settings = service_settings()` runs at import time
in `models/brain.py`, `models/sensor.py`, `api/ui.py` and `services/auth.py`; `authservice` is a
module-level singleton; refresh tokens live in a plain dict on that singleton. This is the same
class of coupling `pvlearn` removed during its own extraction, and it is what makes the code hard to
test in isolation.

**Ingest and training are welded together.** `BrainService.request()`
(`core/learninghouse/services/brain.py:74-110`) appends one row to a CSV, reads the entire CSV back,
and retrains the model — on every single pushed data point.

**Two of four declared sensor types are dead.** `SensorType` declares `NUMERICAL`, `CATEGORICAL`,
`CYCLICAL` and `TIME`, and `SensorConfiguration` carries `cycles` and `calc_sun_position`. Only
numericals and categoricals are ever read (`services/preprocessing.py:22-32`); nothing consumes
cyclical, time, or the sun-position flag.

**There is no pipeline.** Time features are computed at ingest and written into the stored row
(`add_time_information`), one-hot encoding happens via `pd.get_dummies` with manual column
realignment at prediction time, and the imputer is a long-lived object on the brain rather than a
step in a `Pipeline`.

None of this is broken in the sense of failing today. It is, however, the reason each of the
following phases is riskier than it needs to be.

---

## 2. Phase overview

| Phase | Subject | Origin |
|---|---|---|
| 1 | Development environment, toolchain, CI gates | your list #1, extended |
| 2 | Test foundation and de-globalization | added in review |
| 2b | UI test foundation | added in review |
| 2c | uv for the Python build and Docker image | added in review, patterned after `solaredge2mqtt` |
| 3 | Dependency updates | your list #2 |
| 3b | Configuration via `configuration.yaml` / `secrets.yaml` | added in review, patterned after `solaredge2mqtt` |
| 3c | Documentation site | added in review, patterned after `solaredge2mqtt` |
| 4 | Security hardening | added in review |
| 5 | Persistence on SQLite | your list #3 |
| 6 | pvlearn as a library dependency | your list #4 |
| 7 | Sensor types from the pvlearn encoders | your list #5 |
| 8 | Brain on a scikit-learn pipeline | your list #6 |
| 9 | Home Assistant add-on | from the add-on assessment |

Phases 2, 2b, 2c, 3b, 3c and 4 did not come from the original list; they were added during review
and confirmed. The reasoning for each is in its own section.

**One pull request per phase**, matching the convention adopted in `pvlearn`. Commits within a
branch stay individually meaningful; the pull request description carries the reasoning that
survives the squash.

---

## 3. Phases

### Phase 1 — Development environment, toolchain and CI gates

**Goal:** An agent or a new contributor can find out what this project expects without reading the
whole codebase, and CI enforces it.

- `AGENTS.md` as the single source of truth for AI assistants, modelled on the one in `pvlearn`:
  project overview, directory layout, code conventions, testing rules, security guidelines. Tool
  configurations under `.github/` reference it rather than duplicating it.
- `CLAUDE.md` with only the Claude-Code-specific additions, pointing at `AGENTS.md` and at this
  plan.
- Replace `setup.py` / `setup.cfg` / `requirements.txt` / `versioneer.py` with a single
  `pyproject.toml` using `setuptools-scm`, mirroring `pvlearn`. Versioneer is unmaintained and its
  vendored `_version.py` plus the `freeze_version.py` dance in the Docker build exists only to work
  around it.
- Introduce Ruff (lint + format) and Pyright, configured as in `pvlearn` where that makes sense.
- Extend `build_project.yml` with jobs that actually gate: `ruff check`, `ruff format --check`,
  `pyright`, `pytest`. Until Phase 2 lands, the test job is expected to run zero tests — that is
  fine, the point is that the wiring exists before the tests do.
- Decide on the Developer Certificate of Origin (`git commit -s`), as enforced in `pvlearn`.

**Acceptance**
- [x] `pip install -e ".[dev]"`, `ruff check .`, `pyright` and `pytest` all run from a clean clone.
- [x] CI fails on a deliberately introduced lint error and on a deliberately introduced type error.
      Verified locally by introducing both and running the same commands the workflow runs.
- [x] The wheel built from `pyproject.toml` installs and `learninghouse` still starts from the
      console script entry point.
- [x] `versioneer.py`, `_version.py` and `freeze_version.py` are gone and the Docker image still
      reports a correct version at `/api/versions`.

**Note on ordering:** this phase comes first because `AGENTS.md` will document commands
(`ruff check`, `pytest`) that do not exist yet. Documenting them and creating them in the same
phase avoids writing instructions that are wrong the moment they are committed.

---

### Phase 2 — Test foundation and de-globalization

**Goal:** Behaviour is pinned down before anything changes it, and the code is shaped so it can be.

Phase 5 rewrites persistence, Phase 7 changes feature encoding and Phase 8 replaces the estimator.
Each of those silently changes predictions if it goes wrong, and right now nothing would notice.
`pvlearn` treated this as non-negotiable — its Phase 0 existed solely to freeze a reference dataset
and baseline predictions, and the plan there states plainly that without it the extraction was not
verifiable. The same holds here.

**Characterization tests** — capture what the code does today, not what it should do:

- API level: every endpoint under `/api`, with a temporary brains directory as a fixture. Brain
  creation, training, prediction, sensor CRUD, auth flows, error responses.
- A small fixed training dataset committed as a fixture, plus the predictions the current code
  produces from it. This is the learninghouse equivalent of the `pvlearn` baseline and is what
  Phases 7 and 8 will be measured against.
- Preprocessing: `add_time_information`, one-hot alignment between training and prediction,
  the missing-column path in `prepare_prediction`.

**De-globalization** — a precondition for the above, not a separate goal:

- `settings = service_settings()` at module import (`models/brain.py:21`, `models/sensor.py`,
  `api/ui.py:11`, `services/auth.py:28`) becomes a dependency passed in or resolved per request.
  As long as settings are bound at import time, a test cannot point two test cases at two different
  brains directories in one process.
- `authservice` as a module-level singleton likewise. Its in-memory `refresh_tokens` dict is also
  why `workers > 1` cannot work correctly today — see Phase 4.
- `Brain`'s classmethod-and-global style gives way to instances that carry their own paths.

**Coverage:** start with a threshold at whatever the characterization suite reaches, and ratchet it
upward per phase. `pvlearn` gates at 90%; adopting that number on day one here would either block
the phase or invite meaningless tests.

**Acceptance**
- [x] Every `/api` route has at least one test covering the success path and one covering its
      documented error.
- [x] Training and prediction on the fixture dataset are pinned by a test that would fail if the
      predicted values changed.
- [x] Two tests in the same session can use two different brains directories.
- [x] `pytest` runs offline, with no writes outside `tmp_path`.
- [x] A coverage floor is configured in CI and is met.

---

### Phase 2b — UI test foundation

**Goal:** The Angular side gets the same starting discipline Phase 2 gives the Python side, before
Phase 3 touches Angular, TypeScript and Tailwind versions underneath it.

Measured against the current UI: 12 of 48 testable source files have a `.spec.ts` next to them —
roughly a quarter. More importantly, **none of the security-relevant path is covered**:
`shared/guards/auth.guard.ts`, `shared/interceptors/auth.interceptor.ts` and
`modules/auth/auth.service.ts` gate every route and every outgoing request the same way
`EnforceInitialPasswordChange` gates the API in Phase 2, and nothing pins what they do today.
Every service that talks to the backend — `shared/services/api.service.ts`,
`modules/brains/brains.service.ts`,
`modules/configuration/services/sensor-configuration.service.ts` — is equally untested, so Phase 3's
Angular major-version bump and Phase 5's persistence rewrite could each silently change what the UI
sends or how it handles a response, and nothing here would notice.

**A second gap sits in CI, not in the test files.** `build_project.yml` runs `npm install` and
`npm run build:core` for the UI job; it never runs `npm test`. The 12 specs that already exist are
not enforced anywhere but a developer's own machine — Phase 3's acceptance criterion "the UI builds
and its Karma suite passes" is currently verified by hand. Wiring the existing suite into CI is
lower-risk than writing new tests and belongs at the start of this phase, not the end.

- Add a `test` job to `build_project.yml` running Karma headless (`ChromeHeadless` launcher,
  `singleRun: true`), gating the same way the Python `test` job does — before the UI build step, not
  after.
- **Priority order for new specs, most load-bearing first:**
  1. `auth.guard.ts`, `auth.interceptor.ts`, `auth.service.ts` — what redirects, what gets attached
     to a request, what happens on a 401.
  2. `api.service.ts`, `brains.service.ts`, `sensor-configuration.service.ts` — the request/response
     shapes the UI depends on, characterized the same way the API characterization tests pin the
     server side of the same contract.
  3. The remaining untested pages and dialogs — `login`, `change-password`, `apikeys`,
     `sensors.component`, `brains.component`, `edit-dialog`, `table.component`, `form-response`,
     `delete-dialog`, `yes-no`, `password`, `select`, `input` — following the pattern of the 12
     specs that already exist rather than introducing a new style.
- `karma-coverage` is already a devDependency and already writes an HTML report
  (`karma.conf.js:coverageReporter`), but nothing reads it — there is no `check` threshold. Add one,
  set at whatever this phase's suite reaches, mirroring the Python coverage-floor decision in
  Phase 2 and the open question in chapter 5, point 4.
- Stay on Karma/Jasmine for this phase. A runner migration is a separate, larger decision the plan
  does not make here — introducing new specs on a runner about to be replaced would mean writing
  them twice.

**Acceptance**
- [x] `npm test` runs headless and exits non-zero on a failing spec; wired into
      `build_project.yml` and gating the UI build. `check-ui` job runs
      `npm test -- --watch=false --browsers=ChromeHeadlessCI --code-coverage`; `build-ui` now
      depends on it. Verified locally: `ChromeHeadlessCI` (no-sandbox) launcher runs headless,
      and dropping the coverage floor's threshold to an unreachable number reproduces a non-zero
      exit.
- [x] `auth.guard.ts`, `auth.interceptor.ts` and `auth.service.ts` each have a spec covering their
      documented behaviour, success and failure.
- [x] `api.service.ts`, `brains.service.ts` and `sensor-configuration.service.ts` each have a spec
      pinning the requests they issue and how they handle a response.
- [x] A coverage threshold is configured in `karma.conf.js` and is met: 68/53/56/67%
      (statements/branches/functions/lines), the suite's actual measured coverage rounded down
      for margin, mirroring the Phase 2 coverage-floor decision. Next ratchet point is Phase 3,
      same as the Python floor.

The priority-3 list (`login`, `change-password`, `apikeys`, `sensors.component`,
`brains.component`, `edit-dialog`, `table.component`, `form-response`, `delete-dialog`, `yes-no`,
`password`, `select`, `input`) is also covered now, following the existing 12 specs' shallow
"should create" convention rather than the deeper behavioural style used for the priority-1/2
files above. Adding these pulled more source under coverage instrumentation than the specs
exercise, which is why the floor above is lower than the number Phase 2b started with
(73/64/61/72%) — the suite covers more surface, not less.

---

### Phase 2c — uv for the Python build and Docker image

**Goal:** Faster, reproducible Python installs, with CI cache hits that key off a lockfile instead
of pip's per-run wheel cache — the same setup `solaredge2mqtt` already runs.

Placed before Phase 3 rather than after: Phase 3 re-pins every shared dependency against `pvlearn`.
Doing that pinning once, directly in a `uv.lock`, is cheaper than pinning with pip first and moving
the result to uv afterwards.

- `core/pyproject.toml` stays the single source of truth for dependencies; add a committed
  `uv.lock` and drop `setup.py`-era assumptions that no longer apply (there are none left after
  Phase 1, this is here as a sanity check, not new work).
- CI (`check-core`, `build-core` in `build_project.yml`): replace `actions/setup-python` +
  `pip install -e ".[dev]"` + the manual `actions/cache` block over `~/.cache/pip` with
  `astral-sh/setup-uv` and `enable-cache: true`, `uv sync --locked` / `uv run`. The lockfile hash
  becomes the cache key instead of `pyproject.toml`'s hash, which is coarser than what pip currently
  keys on. `save-cache: ${{ github.event_name != 'pull_request' }}`, matching `solaredge2mqtt`: a
  cache written from a PR run is only ever read back by a re-run of that same PR, so writing one on
  every PR push is pure cache-quota spend for no reuse. `build-core` drops the separate "install
  build package" step entirely — `uv build` replaces `pip install build && python -m build`.
- `docker/Dockerfile`, matching `solaredge2mqtt`'s pattern directly rather than just replacing `pip`
  with `uv pip` one-for-one: the `buildimage` stage now syncs dependencies from `core/uv.lock` first
  (`uv sync --frozen --no-install-project`, under a BuildKit `--mount=type=cache` so the download
  cache survives across builds), then installs the wheel on top with `uv pip install --no-deps`, so
  a dependency-only change and a version-only rebuild invalidate different, independently cached
  layers. `python:3.13-slim` replaces `python:3.13` for the build stage too (`solaredge2mqtt` runs
  the build stage on `-slim` throughout); `UV_LINK_MODE=copy` (safe across the layer boundary this
  stage's output crosses into `stage-1`), `UV_PYTHON_DOWNLOADS=never` (use the image's own
  interpreter, don't let `uv` fetch one) and `UV_PROJECT_ENVIRONMENT=/venv` (point the sync straight
  at the venv path the final stage copies out, no separate `uv venv` step). `uv` itself copied in via
  the `ghcr.io/astral-sh/uv` distroless copy trick. The Docker build-push step gets the matching
  `cache-from: type=gha` / `cache-to: type=gha,mode=max`, the latter gated the same way as
  `save-cache` above — only push/release builds write it.
  **Drop the `piwheels` index entirely, matching `solaredge2mqtt`.** It exists only to serve
  prebuilt `armv6l`/`armv7l` wheels for `numpy`/`scipy`/`scikit-learn` — confirmed by `uv`'s own
  resolver error when the index was kept: it lists `numpy` for `linux_armv6l`/`linux_armv7l` only,
  not for the platform actually being built. Phase 9 already excludes `armv7` as a decision taken
  up front (see its multi-architecture section), and Phase 9's `aarch64` target gets manylinux
  wheels straight from PyPI, so nothing here still needs it. Without `armv7` as a target, keeping
  `piwheels` would have meant carrying a `uv`-specific `--index-strategy unsafe-best-match`
  workaround for an index the image no longer needs at all — removed instead of worked around.
- `docker/.dockerignore` widens from `!dist/*.whl` only to also allow `pyproject.toml` and `uv.lock`
  into the build context, and `build_project.yml`'s `build-docker` job copies both from `core/` into
  `docker/` before the build step — the lockfile-sync layer above needs its own copy since the
  Docker build context stays scoped to `docker/`, not the repository root.
- `AGENTS.md` developer commands (`pip install -e ".[dev]"`, etc.) updated to their `uv` equivalents.
- **Multi-architecture build, pulled forward from Phase 9.** Originally scoped there, moved up once
  dropping `piwheels` (above) raised the question of whether `arm64` still needed to wait: it
  doesn't. Checked directly against PyPI — `numpy`, `pandas`, `scikit-learn` and `scipy` all publish
  `manylinux_aarch64` wheels for `cp313` at the versions this project pins, so an `arm64` build never
  needs to compile anything, the same as `amd64`. `build_project.yml`'s `variables` job gains
  `image_name`/`ghcr_image`/`version`/`cache_ref_name` outputs (lowercased once, since `ghcr`/Docker
  Hub reject the mixed case `github.repository` actually carries — `LearningHouseService` — and the
  `merge-manifest` job below builds tags by hand in shell, where `docker/metadata-action`'s automatic
  lowercasing doesn't apply). `build-docker` becomes a `linux/amd64` / `linux/arm64` matrix on native
  runners (`ubuntu-latest` / `ubuntu-24.04-arm` — this repo is public, so both are free GitHub-hosted
  runners), each leg pushing an arch-suffixed tag and exporting its image digest; QEMU is dropped
  entirely since neither leg emulates. A new `merge-manifest` job downloads both digests and combines
  them into the final multi-arch tags with `docker buildx imagetools create`, keyed by digest rather
  than by the mutable per-arch tags so two overlapping workflow runs can't let an older push win.
  Matches `solaredge2mqtt`'s pattern directly (same author, already proven there); the one thing
  *not* adopted from it is its source-copy-instead-of-wheel Dockerfile, for the reason already given
  above — learninghouse bundles the Angular UI into the wheel, `solaredge2mqtt` has no frontend to
  bundle, so the two Dockerfiles' final stage keeps installing a wheel either way.
- Not in scope: changing the runtime dependency *versions* — that is Phase 3. This phase only
  changes the tool that resolves and installs them.

**Acceptance**
- [x] `uv sync` from a clean clone reproduces the same environment `pip install -e ".[dev]"` produced
      before this phase (`ruff check .`, `pyright`, `pytest` all still pass). Verified locally:
      `uv sync --extra dev` then `ruff check .`, `ruff format --check .`, `pyright` and
      `pytest --cov=learninghouse --cov-report=xml:coverage.xml` all pass (70 passed, 85.61%
      coverage, above the Phase 2 floor).
- [x] CI's `check-core` and `build-core` jobs use `astral-sh/setup-uv` with caching enabled.
      Confirmed working on PR #566's CI run (`astral-sh/setup-uv@v10.0.1` — the action publishes no
      floating `v10` tag, only exact releases, `actionlint` caught the wrong pin before a second CI
      run was needed; `cache-dependency-glob: "core/uv.lock"`). The speed-comparison half of this
      criterion needs a *second* run against an *unchanged* lockfile on a cache-writing event —
      `save-cache` is deliberately `false` on `pull_request` events (cache-quota reasoning above), so
      a PR's own re-runs never produce that comparison. Check once this merges and a subsequent push
      to `main` reads back what this PR's merge commit writes.
- [x] The Docker image builds via `uv` and starts identically to the pip-built image (same
      `/api/versions` output, same entry point). Verified locally against the final two-layer
      buildimage (lockfile sync, then wheel installed with `--no-deps`, `piwheels` dropped): built,
      ran it, `curl /api/versions` returned the same payload the pip-built image returned, same
      `python3 -m learninghouse` entry point, same startup log lines.
- [x] `uv.lock` is committed and CI fails if it is out of sync with `pyproject.toml`. `check-core`
      runs `uv sync --extra dev --locked`; verified locally that `--locked` accepts a matching
      lockfile and rejects one made stale by editing a pin in `pyproject.toml` without updating it.
- [x] The `arm64` leg of the Docker build resolves and installs every dependency from
      `manylinux_aarch64` wheels, nothing compiles from source. Verified locally first
      (QEMU-emulated `docker buildx build --platform linux/arm64`, since this machine is `amd64`),
      then confirmed for real on PR #566's CI run: both `build-docker` matrix legs passed on native
      runners (`amd64` on `ubuntu-latest`, `arm64` on `ubuntu-24.04-arm`), 29s each, no QEMU
      anywhere. `merge-manifest` itself correctly skipped on that run (`should_publish` is false for
      a `pull_request` event) — the actual multi-arch manifest push to `ghcr`/Docker Hub still needs
      a push-to-`main` or release event to confirm, which is what `should_publish` is gating it on.

---

### Phase 3 — Dependency updates

**Goal:** Current, coherent dependency set on both sides, with the shared packages already aligned
to what `pvlearn` pins.

- Merge or close the open Dependabot branches (14 as of 2026-08-14, spanning GitHub Actions, npm and
  pip — up from nine when this plan was first written; the backlog grows if left unmerged, so this
  bullet is not a one-time cleanup, it is the reason this phase exists now rather than later).
  `#514` (`scikit-learn` 1.8.0 → 1.9.0) already does this phase's load-bearing bump — verify
  `BrainNotActual` per the risk below before merging it rather than redoing the bump from scratch.
  `#511` (`typescript` 5.9.3 → 6.0.3) is a major version; confirm it compiles against the pinned
  Angular 21 toolchain before merging, don't wave it through with the patch-level bumps.
  - A second backlog of thirteen had accumulated by 2026-08-29 and was cleared the same way; see the
    acceptance criterion below. The prediction in this bullet held: the queue refills whenever it is
    left alone.
- Angular and the npm toolchain to current. Done twice: v21 during the first pass, then v21 → v22
  on 2026-08-29 (`#588`), which dragged `typescript` to `~6.0.3` because
  `@angular-devkit/build-angular@22` declares `peer typescript@">=6.0 <6.1"`. `ngx-translate`
  17 → 18 (`#589`) came with it — v18 drops the NgModule API, so `TranslateModule` had to become
  `provideTranslateService()` plus the standalone `TranslatePipe` across `AppModule`,
  `SharedModule` and 22 specs.
  - **Framework majors are not Dependabot's job.** Both of the above needed migration schematics or
    hand-written API changes that a version bump alone cannot produce. Dependabot's PRs for them
    (`#570`–`#572`, `#578`, `#583`, `#587`) could never go green and were closed in favour of
    branches that ran `ng update` / rewrote the call sites.
  - `typescript` is now bounded from above by whatever Angular's build tooling accepts. TS 7.0.2
    exists and Dependabot will keep proposing it (`#586`, closed); it cannot land before Angular
    supports it.
- Python dependencies to current — **with one constraint that shapes this phase**: `pvlearn` pins
  its dependencies *exactly*, not as ranges. Once Phase 6 adds `pvlearn` to `install_requires`, pip
  will refuse any different pin of a shared package. In practice learninghouse inherits pvlearn's
  pins for `numpy`, `pandas`, `scipy`, `scikit-learn`, `pydantic` and `joblib`. Aligning them here
  keeps Phase 6 a one-line change instead of a resolution fight.

  | Package | learninghouse at phase start | pvlearn pin then | both sides on 2026-08-29 |
  |---|---|---|---|
  | `numpy` | 2.4.4 | 2.5.1 | 2.5.2 |
  | `pandas` | 3.0.3 | 3.0.5 | 3.0.5 |
  | `scipy` | — | 1.18.0 | 1.18.1 |
  | `scikit-learn` | 1.8.0 | 1.9.0 | 1.9.0 |
  | `pydantic` | 2.13.4 | 2.13.4 ✓ | 2.13.4 |
  | `joblib` | 1.5.3 | 1.5.3 ✓ | 1.5.3 |

  The third column is the point: `numpy` and `scipy` have both moved on since this phase closed
  (`#569`, `#581`), and pvlearn moved with them, so the pins still match. They will keep moving.
  Whoever merges a shared-package bump here has to check pvlearn's `pyproject.toml` in the same
  breath — Dependabot has no idea this constraint exists.

- **The scikit-learn bump is the one with consequences.** `pvlearn`'s frozen baseline is only
  reproducible against exactly 1.9.0 (chapter 6.6 of the pvlearn plan), so this pin is load-bearing
  on that side. On this side, existing trained brains were produced by 1.8.0. Verify that the
  existing version check (`BrainNotActual`) actually covers the scikit-learn version and forces a
  retrain — if it only compares the service version, brains trained under 1.8.0 will keep being
  loaded and silently mispredict.
- Replace `passlib` (`models/auth.py:9`, `sha512_crypt`). Its last release was 2020 and it is
  effectively unmaintained. Move to `argon2-cffi` or `bcrypt`, rehashing on the next successful
  login so existing passwords keep working. Can also be taken in Phase 4 — it belongs to both.

**Acceptance**
- [x] Dependabot backlog is empty. Fourteen open branches at the start of this phase, down to one
      (`#514`, scikit-learn 1.8.0 → 1.9.0) after the coordinated Angular bump (`e2323cb`) and the
      dependabot.yml fix (`8653b32`); `#514` closed as superseded once `d3e4692` pinned
      `scikit-learn==1.9.0` directly alongside the other shared pins. Emptied a second time on
      2026-08-29: `#569`, `#573`, `#574`, `#579`, `#580`, `#581`, `#584`, `#585` merged;
      `#570`–`#572`, `#578`, `#583`, `#586`, `#587` closed in favour of `#588` and `#589`. The
      npm ecosystem in `.github/dependabot.yml` grew an `angular` group (`#582`) so a framework
      major arrives as one installable PR instead of per-package bumps that each fail `npm ci`
      with `ERESOLVE`.
- [x] The characterization suite from Phase 2 passes unchanged, or every deviation is explained and
      the baseline deliberately regenerated. Verified locally: `uv run pytest
      --cov=learninghouse --cov-report=xml:coverage.xml` — 71 passed, 85.78% coverage (above the
      85% floor), including `test_baseline.py::TestBaseline::test_prediction_on_a_fixed_input_is_pinned`
      unchanged. Re-verified on 2026-08-29 after the second backlog and the Phase 3b work:
      `uv run pytest` in `core/` — 93 passed.
- [x] Shared pins match `pvlearn` exactly, verified by installing both into one environment.
      Verified locally by diffing the pin lists, re-checked on 2026-08-29 after `#569` and `#581`:
      `numpy==2.5.2`, `pandas==3.0.5`, `scipy==1.18.1`, `scikit-learn==1.9.0`, `pydantic==2.13.4`,
      `joblib==1.5.3` in both `core/pyproject.toml` and pvlearn's `pyproject.toml` (`4be14d8`).
      A real single-environment install of both packages together is Phase 6's job, once pvlearn
      is actually a dependency here.
- [x] A brain trained before the update is either loaded correctly or rejected with a clear message
      and retrained — never loaded best-effort. Covered by
      `test_brain.py::TestPredictionPost::test_brain_trained_under_different_library_versions_is_rejected`
      and the `Brain.actual_versions` / `BrainNotActual` unit tests added in `3c2a28a`; both pass.
- [x] The UI builds and its Karma suite passes. Verified locally: `npm test -- --watch=false
      --browsers=ChromeHeadlessCI --code-coverage` — 87/87 SUCCESS, coverage above the Phase 2b
      floor (68/53/56/67%); `npm run build:core` completes cleanly. Re-verified on Angular 22 and
      ngx-translate 18 — still 87/87, but coverage now clears the floor by a rounding step
      (statements 68.13% against 68%, lines 67.2% against 67%). The next change that touches
      untested code turns `check-ui` red on the thresholds, not on a failing test.

---

### Phase 3b — Configuration via `configuration.yaml` / `secrets.yaml`

**Goal:** Replace the environment-variable-driven settings with a `configuration.yaml` plus a
separate `secrets.yaml` for sensitive values — the model `solaredge2mqtt` already uses, and the one
Phase 9's Home Assistant add-on will want to read from its mapped `/data` directory anyway.

`ServiceSettings.__init__` (`core/learninghouse/core/settings/models.py`) currently merges three
sources in order: `_read_environment`, `_read_dotenv`, `_read_secrets` (Docker secrets under
`/run/secrets`). All three are ways of avoiding one readable file; a `configuration.yaml` is that
file, and separating `secrets.yaml` keeps the split Docker secrets already made (config vs.
sensitive values) without needing the Docker-specific mechanism.

- `ServiceSettings` reads `configuration.yaml` for everything currently settable via `LEARNINGHOUSE_*`
  (`host`, `port`, `workers`, `logging_level`, CORS origins from Phase 4, …), and `secrets.yaml` for
  `jwt_secret` and anything else that should never be readable from the general config file or from
  logs.
- One bootstrap value has to stay resolvable before either YAML file can be located:
  `config_directory` (or an explicit path to `configuration.yaml`) remains settable via a single
  environment variable, matching how `solaredge2mqtt` bootstraps its own config path. Everything
  downstream of that path moves to YAML.
- **`jwt_secret` gets its persistent home here, not in Phase 5.** Today it defaults to a fresh
  `token_hex(16)` per process start (`core/settings/models.py:39`); Phase 4 originally proposed
  persisting it via the Phase 5 SQLite database. Writing it into `secrets.yaml` on first start
  achieves the same thing without waiting on Phase 5, and is simpler — the value never becomes a
  table for one row. Phase 4's acceptance criterion ("sessions survive a restart") is satisfiable
  starting in this phase.
- `docker/Dockerfile` currently hardcodes `LEARNINGHOUSE_HOST=0.0.0.0` and `LEARNINGHOUSE_PORT=5000`
  as image `ENV` values. Replace with a documented default `configuration.yaml` baked into the image
  (or written on first start if the mounted volume doesn't have one), overridable by mounting a file
  over it.
- **Migration for existing installations: a one-shot script, not a runtime fallback.** Reading
  `LEARNINGHOUSE_*` as a permanent deprecated fallback keeps two settings paths alive indefinitely
  and defeats the point of this phase. Instead, ship a migration script (`core/scripts/` or a
  console entry point, e.g. `learninghouse-migrate-config`) that reads every `LEARNINGHOUSE_*`
  variable currently set in the process environment (and `.env` if present) and writes them into a
  `configuration.yaml` / `secrets.yaml` pair at the target `config_directory`. Run once, by hand, on
  upgrade — not on every start.
  - Must be idempotent-safe to re-run: refuses to overwrite an existing `configuration.yaml` /
    `secrets.yaml` unless passed an explicit `--force`, so re-running it after a manual edit doesn't
    silently clobber it.
  - Splits sensitive values (`jwt_secret`, anything else Phase 3b routes to `secrets.yaml`) from the
    rest correctly — same split the settings loader itself uses, driven by one shared field list so
    the two can't drift apart.
  - Console form: run directly against a `config_directory` on disk, e.g.
    `learninghouse-migrate-config --config-directory ./brains`.
  - Docker form: run once inside the container against the mounted volume before switching the image
    to the version that requires YAML config, e.g.
    `docker run --rm --env-file .env -v <volume>:/learninghouse/brains <image> learninghouse-migrate-config`,
    reusing the same `.env`/`LEARNINGHOUSE_*` variables the old container was started with.
- **README.** Document both invocation forms above, plus what the script does and does not migrate
  (env vars only — it does not touch brain data, sensors or the security database), as part of this
  phase, not deferred to Phase 9. Section 4's versioning discipline already expects a changelog entry
  for a breaking change; this is one.

**Acceptance**
- [x] Every setting currently readable from a `LEARNINGHOUSE_*` environment variable is readable from
      `configuration.yaml`. `ServiceSettings.__init__` merges every top-level key of
      `configuration.yaml` (except `config_directory` and `SECRET_FIELDS`) the same way the old
      generic env-var reader did; covered by `tests/core/test_settings.py::TestConfigurationYaml`.
- [x] `jwt_secret` (and any other sensitive value) is read only from `secrets.yaml`, never from
      `configuration.yaml`, the environment, or logged output. `SECRET_FIELDS` is excluded from the
      `configuration.yaml` merge in code; `test_jwt_secret_in_configuration_yaml_is_ignored` and
      `test_other_learninghouse_env_vars_are_no_longer_read` pin this. Grepped
      `services/auth.py` - `settings.jwt_secret` is only ever passed to `jwt.encode`/`decode`, never
      logged or printed.
- [x] `jwt_secret` persists across a service restart without depending on Phase 5. Generated once and
      written to `secrets.yaml` (`0600`) on first read; `test_the_jwt_secret_survives_across_restarts`
      pins two `ServiceSettings` instances against the same directory. Verified against a real restart
      too, via the Docker check below (`secrets.yaml` on the bind-mounted volume survived the
      container being stopped and a fresh container started against the same volume).
- [x] The Docker image starts correctly with only a mounted `configuration.yaml`, no `LEARNINGHOUSE_*`
      environment variables set. Verified locally: built the image (`docker/configuration.yaml` now
      baked in at `/learninghouse/brains/configuration.yaml`, the `LEARNINGHOUSE_HOST`/`_PORT` image
      `ENV` lines removed), ran it with zero environment variables and no mount - `/api/versions`
      returned 200 using the baked-in default (`host: 0.0.0.0`, `port: 5000`). Ran it again with a
      volume mounted over `/learninghouse/brains` containing a `configuration.yaml` with a custom
      `title` - the mounted file's values won, and `secrets.yaml` (`0600`) was written to the mounted
      volume, not just image-local storage.
- [x] The migration script converts a representative set of `LEARNINGHOUSE_*` variables (including at
      least one that must land in `secrets.yaml`) into a correct `configuration.yaml` /
      `secrets.yaml` pair, verified against a fixture of the old environment-variable layout.
      `tests/scripts/test_migrate_config.py::TestMigrate::test_writes_a_correct_configuration_and_secrets_pair`.
- [x] The migration script refuses to overwrite existing YAML files without `--force`.
      `test_refuses_to_overwrite_without_force` / `test_force_overwrites_an_existing_pair`.
- [x] README documents console and Docker invocation of the migration script, and the changelog
      records the breaking change. See README "Upgrading from `LEARNINGHOUSE_*` environment
      variables" and `CHANGELOG.md`'s Unreleased section.

---

### Phase 3c — Documentation site

**Goal:** A published documentation site built from `docs/` with MkDocs Material, the way
`solaredge2mqtt` does it, replacing the single 310-line `README.md` that currently carries every
piece of user-facing documentation this project has.

Everything a user needs — configuration keys, the migration script from Phase 3b, sensor and brain
configuration, training and prediction examples, Docker instructions — lives in one Markdown file
that is read on a repository page. It has no navigation, no search, no dead-link checking, and a
change to any of it is invisible in review beyond the diff. The later phases make this worse rather
than better: Phase 4 adds CORS and session settings, Phase 5 changes where data lives, Phase 9 adds
an add-on with its own installation path. Splitting the file after those phases means writing the
same pages twice.

- **`mkdocs.yml` at the repository root**, `docs_dir: docs`, `mkdocs-material` as the theme, with
  the same `validation` block `solaredge2mqtt` uses: `unrecognized_links: warn` and
  `anchors: warn`, so a link to a heading somebody renamed fails the build instead of quietly
  landing at the top of the page.
- **Documentation dependencies as a `docs` extra in `core/pyproject.toml`**, pinned exactly like
  the `dev` extra already is, and resolved through `core/uv.lock`. This project keeps its Python in
  `core/` while the documentation sits at the root, so the build runs as
  `uv run mkdocs build --strict --config-file ../mkdocs.yml` from `core/`. A second lockfile at the
  root purely for two documentation packages was rejected — it would be the only Python project
  outside `core/` and would need its own dependency updates.
- **Split the README into pages.** Proposed nav, following the shape of the existing headings:
  - *Getting Started*: installation, first configuration, running the service
  - *Configuration*: `configuration.yaml` / `secrets.yaml` reference, sensors, brains, security
    (fallback password, API keys)
  - *Usage*: training, prediction, the UI, where the API documentation lives
  - *Deployment*: Docker, Docker Compose
  - *Migration*: `LEARNINGHOUSE_*` environment variables (the Phase 3b section, moved verbatim)
  - *Troubleshooting*
  - *Reference*: architecture decisions
- **The README keeps only what a repository page is for**: badges, what the service does, the
  feature list, a quick start, and a prominent link to the site. `solaredge2mqtt`'s README is 87
  lines against this project's 310.
- **Do not restate the API.** The service already serves its OpenAPI documentation at `/docs`;
  the site links there instead of growing a second, immediately stale copy of the endpoint list.
- **An architecture decision record series**, `docs/decisions/`, with the index table and the
  append-only rule `solaredge2mqtt` uses: numbered `NNNN-kebab-case-title.md`, superseded rather
  than edited. Seed it with the decisions this plan has already made and that the code cannot
  explain by itself — uv for the build (Phase 2c), YAML configuration with a one-shot migration
  instead of an env-var fallback (Phase 3b), the exact-pin coupling to `pvlearn` (Phase 3), and the
  Dependabot grouping that a framework major forced (Phase 3). Writing them now, while the reasoning
  is still recoverable from the pull requests, is the point; after Phase 5 it is archaeology.
- **`docs/modernization-plan.md` is not user documentation.** Either give it a place in the site
  under a clearly internal section, or exclude it via `not_in_nav` so a `--strict` build stays
  clean. Excluding it is the recommendation: this plan is written for the people doing the work,
  and it will read as unfinished promises to anybody else.
- **CI, patterned on `solaredge2mqtt`'s `build_project.yml`**: a `build-docs` job that runs
  `mkdocs build --strict` on every push and pull request and uploads the rendered `site/` as an
  artifact, so a documentation change can be reviewed as a browsable site; plus a `deploy-docs` job
  that publishes to GitHub Pages **on release only**, after the jobs that publish what the site
  describes. A push to `main` can carry documentation for an unreleased version — the published
  site should not.

**Acceptance**
- [x] `mkdocs build --strict` passes and runs in CI on every push and pull request; a dead internal
      link, an unknown anchor or a nav entry pointing at a missing file fails the build. Verified
      locally with `uv run mkdocs build --strict --config-file ../mkdocs.yml` from `core/`: clean
      on the real site, and all three failure modes reproduced deliberately — a link to a
      non-existent page, a link to a non-existent anchor on an existing page (both
      `Aborted with 2 warnings in strict mode!`) and a `nav` entry pointing at a missing file
      (`Aborted with 1 warnings in strict mode!`). The CI half runs in the new `build-docs` job,
      which is triggered by the workflow's existing `push` (main) / `pull_request` / `release`
      events — first real run happens when this branch opens its pull request.
- [x] The rendered site is available as a CI artifact for every run. `build-docs` uploads `site/`
      as `docs-site-${REF_NAME}` unconditionally, and additionally as a Pages artifact on
      `release`.
- [x] The site deploys to GitHub Pages on release only, and after the jobs that publish the package
      and the images it documents. `deploy-docs` is gated on
      `if: ${{ github.event_name == 'release' }}` and needs `[build-core, build-docs,
      merge-manifest]` — `build-core` is what publishes to PyPI and the release assets,
      `merge-manifest` what pushes the multi-arch image tags. `concurrency: group: pages` with
      `cancel-in-progress: false`, so overlapping releases queue rather than leaving the site on a
      previous version. `actions/configure-pages` runs with `enablement: true`, so the first
      release does not need Pages switched on by hand. Not verifiable locally: needs an actual
      release event.
- [x] Nothing that exists only in today's README is lost. Every configuration key, the Phase 3b
      migration instructions, the sensor and brain examples, and the training and prediction calls
      have a page; verified by diffing the old README's headings against the nav. Mapping:
      *Introduction* and *Contact and Feedback* → `index.md`; *Installation and Configuration* /
      *Prepare configuration directory* → `getting-started/installation.md`; *Service
      configuration* / *Example configuration* → `getting-started/configuration.md` and
      `configuration/index.md`; *Upgrading from `LEARNINGHOUSE_*` environment variables* →
      `migration/environment-variables.md` (moved verbatim in substance); *Run the service* →
      `getting-started/running.md` and `deployment/docker.md`; *UI* → `usage/ui.md`; *Security* /
      *Fallback password* / *API Key* → `configuration/security.md`; *Sensors Configuration* →
      `configuration/sensors.md`; *Example brain* / *Configuration Parameters* / *Estimator* /
      *Dependent variable* / *Test size* / *Changing configuration via RESTful API* →
      `configuration/brains.md`; *API Documentation* → `usage/api.md`; *Train the brain* →
      `usage/training.md`; *Prediction* → `usage/prediction.md`. Two corrections were made in the
      move rather than carried over: the old *info* example URL was missing the `/api` prefix the
      router actually mounts, and the persisted-file list now matches `BrainFileType` /
      `sanitize_filename` (`<brain>/training_data.csv`, not `<brain>/data/training_data.csv`) plus
      the `security.json` and `info.json` files the old README never mentioned.
- [x] The README is reduced to overview, features, quick start and a link to the site. 310 lines
      down to 80.
- [x] Documentation dependencies are pinned in `core/pyproject.toml` and locked in `core/uv.lock`,
      and the docs job uses the same `uv` version and flow as the other jobs. `docs = ["mkdocs==
      1.6.1", "mkdocs-material==9.7.7"]` — the same versions `solaredge2mqtt` pins, so the two
      sibling sites render with the same theme release. `build-docs` uses the same
      `astral-sh/setup-uv@v10.0.1`, the same `cache-dependency-glob: "core/uv.lock"` and the same
      `save-cache: ${{ github.event_name != 'pull_request' }}` as `check-core`/`build-core`, then
      `uv sync --extra docs --locked`.
- [x] `docs/modernization-plan.md` is either in the nav or explicitly excluded, and the strict
      build is clean either way. Excluded via `not_in_nav`, as this phase recommended — naming it
      there rather than leaving it unmentioned is what keeps `--strict` from failing on a page in
      `docs/` that no nav entry points at.
- [x] `docs/decisions/` exists with an index table and at least the four seed records named above.
      `0001-uv-for-the-python-build.md` (Phase 2c), `0002-yaml-configuration-with-a-one-shot-
      migration.md` (Phase 3b), `0003-exact-pins-shared-with-pvlearn.md` (Phase 3) and
      `0004-dependabot-groups-for-framework-majors.md` (Phase 3), with the append-only rule and
      the "writing a new one" instructions in the index.
- [x] Every documented configuration key matches the fields `ServiceSettings` actually reads —
      checked against the code, not against the old README. Verified by importing
      `ServiceSettings.model_fields` and diffing it against the key column of
      `docs/configuration/index.md`: no documented key that the model does not read, and the only
      model field absent from the `configuration.yaml` table is `config_directory` — which is
      documented in the same page as the one environment variable, because it is the bootstrap
      value that determines where `configuration.yaml` is read from and therefore cannot be set
      from inside it.

---

### Phase 4 — Security hardening

**Goal:** Close the findings that would otherwise ship into people's homes in Phase 9.

These are small, independent changes, and each of them is harder to make after the add-on exists,
because by then someone is depending on the current behaviour.

- **CORS.** `service.py:52` sets `allow_origins=["*"]` together with `allow_credentials=True`.
  Starlette resolves that combination by reflecting the request's `Origin` header back instead of
  sending a wildcard, which means any web page a user visits can make authenticated requests to
  their learninghouse instance. Replace with a configurable origin list, defaulting to the UI's own
  origin — the list lives in `configuration.yaml` since Phase 3b.
- **API keys in the query string.** `services/auth.py:32` accepts the key via `APIKeyQuery` as well
  as the header. Query strings end up in access logs, proxy logs and browser history. Deprecate the
  query variant, keep the header.
- **JWT secret.** `core/settings/models.py:39` defaults `jwt_secret` to a fresh `token_hex(16)` per
  process start. Consequences: every restart invalidates all sessions, and with `workers > 1` each
  worker generates its own secret, so tokens issued by one worker are rejected by another. Phase 3b
  already persists it in `secrets.yaml`; this phase only needs the warning log for when it had to be
  generated for the first time.
- **Refresh tokens in memory.** `AuthServiceInternal.refresh_tokens` is a per-process dict, which is
  the second half of the same multi-worker problem. Either persist it or document that `workers`
  must stay at 1.
  - **Documented, not enforced, and handed to Phase 5.** A startup refusal of `workers > 1` was
    written in this phase and then removed again: no release ships between here and Phase 5, which
    removes the cause outright, so the guard would have been born and buried without a user ever
    meeting it. The documentation says `workers` must stay at `1` and why.
  - This is the reported symptom in
    [#306](https://github.com/LearningHouseService/learninghouse/issues/306) ("JWT refresh not
    working reliably" - a refresh that works, then fails seconds later). The answer given there was
    Redis (#373, closed); the shared storage this plan brings instead is Phase 5's SQLite. Phase 3b
    closed the regenerated-secret half of the symptom; Phase 5 closes the rest. The issue stays open
    until then.
  - The dictionary is not the only per-process state in the way: `AuthServiceInternal` reads
    `security.json` once in its constructor and is cached for the life of the process, so a
    password change or a new API key made through one worker is invisible to the others. Both have
    to move in Phase 5.
- Password hashing per Phase 3, if not already taken there. It was not - it is taken here.

**Acceptance**
- [x] A cross-origin credentialed request from an origin that is not configured is rejected.
      `allow_origins=["*"]` is gone; `cors_allowed_origins` in `configuration.yaml` defaults to the
      service's own origin (`ServiceSettings.cors_origins`) and refuses `*` outright, because a
      wildcard next to `allow_credentials=True` makes Starlette reflect the request's own `Origin`.
      Pinned by `tests/test_service.py::TestCors` - an unconfigured origin gets no
      `Access-Control-Allow-Origin` header and its credentialed preflight is answered with `400` -
      and by `tests/core/test_settings.py::TestCorsOrigins`.
- [x] Sessions survive a service restart. Delivered in Phase 3b (`jwt_secret` in `secrets.yaml`,
      `test_the_jwt_secret_survives_across_restarts`); this phase adds the warning log for the
      start that had to generate it, asserted not to contain the secret itself by
      `tests/test_secret_logging.py::TestJwtSecretGeneration`.
- [ ] `workers > 1` either works correctly or is rejected at startup with an explanation.
      **Deliberately not met here.** The refusal existed in this branch and was removed: it only
      protects the window between this phase and Phase 5, and no release falls into that window.
      Phase 5 removes the cause instead - its acceptance criteria now carry the criterion, including
      the second blocker (the security database read once per process) that this phase uncovered.
      What remains here is documentation: `workers` must stay at `1`, and why.
      `learninghouse.__main__` still turns an invalid configuration into a readable message and exit
      code `1` rather than a pydantic traceback, which the wildcard-origin refusal needs anyway.
- [x] No secret, token or API key appears in log output at any level.
      `tests/test_secret_logging.py` attaches a loguru sink at `DEBUG`, runs a full administration
      flow (login, password change, API key creation, use, listing and deletion) and asserts that
      the password, the API key, `jwt_secret` and both tokens are absent from everything written.

**Beyond the listed bullets**
- API keys are hashed with a salted SHA-256 rather than `sha512_crypt` at 400,000-999,000 rounds.
  The password hash's cost was being paid on every prediction request, against a 128-bit key that
  no one guesses; it also gave any unauthenticated caller a cheap way to spend the service's CPU.
- **The old hash format is not read at all, `passlib` is gone, and nothing migrates the old
  credentials.** Verifying the old hashes would have kept an unmaintained dependency alive
  indefinitely, since nothing forces an installation to log in again; resetting them on load was
  written and then removed for the same reason the worker guard was - Phase 5 creates the security
  store from scratch, and no release falls between the two. Breaking change at that release,
  recorded in the changelog and on the security page - see decision 0006.
- `/api/versions` reports `argon2` where it reported `passlib`; `argon2-cffi-bindings` is pinned
  explicitly next to `argon2-cffi`, because that is the half carrying the C implementation.
- A rejected API key and a rejected administration login now write a warning naming neither value.
  Guessing is bounded by the request rate, not by the hash, and until this the attempts left no
  trace at all. A rate limit for the authentication surface is a separate piece of work.
- The condition the API key hashing depends on - server-generated, 128 bits, no client-supplied
  keys - is pinned by `tests/models/test_auth.py::TestApiKeyEntropy` rather than left implicit.
- `SecurityDatabase.salt` was a class-level `token_hex(8)`, evaluated once per process, so every
  database created by one process shared a salt. It is a `default_factory` now.

---

### Phase 5 — Persistence on SQLite

**Goal:** One storage mechanism instead of four, with a schema that will still fit when training
data becomes a time series.

Today: brain configuration in `config.json`, sensors in `brains/sensors.json`, training data in
`brains/<name>/data/training_data.csv`, the security database in its own JSON file, and the trained
model as a pickle. Reading a single training row means loading the entire CSV; appending one means
rewriting it.

- Single SQLite database in the configuration directory. Tables for brains, sensors, training data
  and security/API keys. The JWT secret does *not* move here — it stays in `secrets.yaml` since
  Phase 3b, deliberately outside the database that gets backed up/inspected alongside brain data.
- **Design the training-data table for time series now.** A timestamp column, a uniqueness
  constraint on it, and idempotent upsert. This costs nothing today and is exactly what the later
  pvlearn integration needs: weather snapshots written ahead of time, the measured target value
  arriving an hour later, and possible backfilling of history. Retrofitting it after brains exist in
  the field means a migration of live data.
- **Decouple ingest from training.** `BrainService.request()` currently retrains on every pushed
  row. That is survivable for a RandomForest over a few hundred rows and is not survivable for the
  pipeline arriving in Phase 8. Split into "store a row" and "train", with training triggered
  explicitly.
- One-shot migration on startup: read the existing JSON and CSV files, write them into SQLite, move
  the originals aside rather than deleting them. Must be idempotent and must be covered by tests
  against a fixture of the old layout.
- Schema versioning via `PRAGMA user_version` and a small migration runner. See open decisions.
- **Restoring multi-worker support is part of this phase, not a side effect.** Two pieces of
  per-process state stand in the way, and the tables here are what remove them: refresh tokens
  (`AuthServiceInternal.refresh_tokens`, a plain dictionary) and the security database, which is
  read once per process in that service's constructor and therefore never sees another worker's
  password change or new API key. Phase 4 deliberately left this alone rather than building a
  second storage mechanism one phase early; this is where
  [#306](https://github.com/LearningHouseService/learninghouse/issues/306) can be closed.
- **The security tables start empty.** The `sha512_crypt` credentials of releases before Phase 4
  cannot be read, so nothing is migrated from `security.json`: the schema is created with the
  initial administration password and no API keys, and the release says so. Everything else -
  brains, sensors, training data - is migrated as described above.

**Acceptance**
- [ ] `workers > 1` starts and works: a session issued by one worker is accepted by every other
      one, and a password change or new API key made through one is effective in all of them
      without a restart.
- [ ] The security store is created empty, with the initial administration password, and the
      release documents that credentials are not carried over.
- [ ] A configuration directory in the old layout is migrated on first start, and the service
      behaves identically afterwards — verified against the Phase 2 characterization suite.
- [ ] Migration run twice changes nothing the second time.
- [ ] Pushing a training row no longer triggers training.
- [ ] Two rows with the same timestamp result in one stored row, not two.
- [ ] No `.csv` or `.json` is written at runtime any more.

---

### Phase 6 — pvlearn as a library dependency

**Goal:** `pvlearn` is installed and importable. Nothing else.

Explicitly *not* in this phase: weather adapters, scheduling, a PV brain type, horizon predictions.
Those belong to the integration plan that follows this one.

- Add `pvlearn` to the dependencies.
- Confirm the shared pins from Phase 3 resolve in one environment.
- Confirm the version report at `/api/versions` picks up pvlearn.

**Acceptance**
- [ ] `pip install learninghouse` installs pvlearn, and both import in the same process.
- [ ] The full test suite passes with pvlearn present.
- [ ] Nothing in learninghouse imports from pvlearn yet, except the version report.

---

### Phase 7 — Sensor types from the pvlearn encoders

**Goal:** The sensor types that are declared actually work, using pvlearn's encoders rather than a
second implementation.

`SensorType.CYCLICAL` and `SensorType.TIME` exist in the enum, and `SensorConfiguration` carries
`cycles` and `calc_sun_position`, but `DatasetPreprocessing.sensorsconfig()` only ever reads
`categoricals` and `numericals`. The configuration surface is there; the behaviour behind it is not.

- Wire `CYCLICAL` to pvlearn's `CyclicalEncoder`, using the existing `cycles` field. This is the
  encoder that fixes wind direction, azimuth and any other wrap-around quantity, where the current
  treatment as a plain numerical makes 359° and 0° maximally distant.
- Wire `TIME` to pvlearn's `TimeEncoder`, replacing `add_time_information`. Today the time features
  are computed at ingest and stored in the row, which means they are frozen into the training data
  and cannot be changed without rewriting history. As an encoder they become part of the model
  instead.
- Wire `calc_sun_position` to pvlearn's `SunEncoder`. It takes primitive `latitude`, `longitude` and
  `timezone` parameters, so the location becomes an explicit brain property.
- **`datetime.fromtimestamp()` in `add_time_information` uses the process's local timezone.** With
  `SunEncoder` requiring an explicit timezone anyway, this is the moment to make timezone a brain
  property rather than an ambient one. The pvlearn plan names this as its most likely source of
  error during the equivalent change.

**Two defects found in this area, to be fixed here:**

- `services/preprocessing.py:38` formats the datetime with `"%Y-%m-%d %H:%M:%s"`. Lowercase `%s` is
  a glibc extension meaning epoch seconds, not seconds within the minute. The stored `datetime`
  column therefore contains a full epoch timestamp where the seconds should be.
- `train_test_split(..., random_state=0)` in `prepare_training` shuffles by default. For brains
  whose rows are timestamped and autocorrelated, neighbouring samples land on both sides of the
  split and the reported accuracy comes out optimistic. The same defect exists in pvlearn's
  `PFISelector` and is recorded there as a known issue; whichever project fixes it first should
  record the reasoning once and the other should reference it.

**Acceptance**
- [ ] A cyclical sensor at 359° and one at 1° are close in feature space.
- [ ] Time features are produced by the pipeline, not stored in the training data.
- [ ] A brain configured with a location produces sun-position features for a known date and place,
      verified against known values.
- [ ] Two brains in two different timezones behave correctly in the same process.
- [ ] Prediction quality on the Phase 2 fixture is not worse than the baseline, within a tolerance
      stated in the pull request.

---

### Phase 8 — Brain on a scikit-learn pipeline

**Goal:** The brain becomes a real `Pipeline`, comparable to pvlearn's `Forecaster`, with
`HistGradientBoostingRegressor` replacing `RandomForest`.

- Encoding, imputation and the estimator become steps of one `Pipeline` object. Today
  `pd.get_dummies` runs at preprocessing time and prediction realigns columns by hand
  (`prepare_prediction`, via `reindex(columns=..., fill_value=0)`); a `OneHotEncoder` with
  `handle_unknown="ignore"` inside a pipeline does this correctly by construction.
- The imputer stops being a long-lived object hanging off the brain and becomes a pipeline step,
  fitted with the rest.
- `RandomForestClassifier` / `RandomForestRegressor` give way to
  `HistGradientBoostingClassifier` / `HistGradientBoostingRegressor`.
- `BrainEstimatorConfiguration` currently exposes `estimators` and `max_depth`, which are
  RandomForest parameters. Decide their fate: map to the nearest equivalents, deprecate, or replace
  with the parameters that actually matter for the new estimator. Existing brain configurations in
  the field carry these fields.
- Model metadata and hard invalidation, following chapter 3.4 of the pvlearn plan: a mismatch in
  schema version, scikit-learn minor version or estimator type means the model is rejected and
  retrained, never loaded best-effort.

**Acceptance**
- [ ] Training and prediction go through a single `Pipeline` object; no manual column realignment
      remains.
- [ ] Prediction quality on the Phase 2 fixture is not worse than the baseline, within a stated
      tolerance.
- [ ] A model persisted by the previous version is rejected with a clear message and retrained.
- [ ] An unseen category at prediction time does not raise and does not shift the other columns.

---

### Phase 9 — Home Assistant add-on

**Goal:** learninghouse installs from a Home Assistant add-on repository, runs under Ingress and
survives restarts and updates with its data intact.

Decisions already taken for this phase: Ingress rather than a plain port; Ingress requests are
trusted because Home Assistant has already authenticated the user; `amd64` and `aarch64` only.

**Multi-architecture build — done early, in Phase 2c, not here.** Pulled forward once the piwheels
drop and the wheel-availability check in that phase confirmed there was no longer a reason to wait:
every dependency (`numpy`, `pandas`, `scikit-learn`, `scipy`) has `manylinux_aarch64` wheels for
cp313 on PyPI, so nothing needs to compile on `arm64` either — the QEMU-emulation slowness that
made this feel like a Phase 9 concern was never actually about wheel availability, just about
`armv7`, which Phase 2c already dropped. `build-docker` is now a `linux/amd64` /
`linux/arm64` matrix on native runners (`ubuntu-latest` / `ubuntu-24.04-arm`, no QEMU), with a
`merge-manifest` job combining both by digest. `armv7` stays unsupported, consistent with the
pvlearn plan, which excludes it for the same wheel-availability reason. That limitation belongs
prominently in the documentation — still this phase's job, see below.

**Ingress path handling.** Home Assistant serves add-ons under `/api/hassio_ingress/<token>/` and
sets an `X-Ingress-Path` header. Three places break:

- `api/ui.py:26` redirects to the absolute path `/ui`.
- `get_env()` builds the UI's API URL from `request.base_url`, which does not carry the ingress
  prefix.
- FastAPI's `root_path` is never set. The installed `ProxyHeadersMiddleware` handles
  `X-Forwarded-For` and `X-Forwarded-Proto`, not a path prefix.

Add middleware that sets `scope["root_path"]` from the header, make redirects relative, and derive
the UI's API URL from the prefixed base.

**Authentication under Ingress.** Requests arriving through Ingress skip the login and the initial
password enforcement, because Home Assistant has already authenticated the user. Direct access to
the exposed port keeps the existing protection. **The ingress header must only be honoured when the
request originates from the Supervisor** — otherwise anyone able to reach the port can set the
header themselves and bypass authentication entirely. Verify the peer address, do not trust the
header alone.

**Packaging.**

- Add-on repository under `LearningHouseService/hassio-addons`, or the add-on added to an existing
  one.
- `config.yaml` with options for log level, port and CORS origins; `ingress: true`; `map: [data:rw]`
  with the bootstrap config path from Phase 3b pointed at `/data`. The add-on's options translate
  into the `configuration.yaml` written to that mount rather than into environment variables — the
  natural use case Phase 3b was built for. `secrets.yaml` on the same mount also gives Home
  Assistant's own `!secret` convention a familiar counterpart on this side.
- A watchdog URL. `/api/mode` exists and would serve, though a dedicated `/health` that does not
  touch auth state is cleaner.
- Decide between the current standalone Dockerfile and the Home Assistant Python base images with
  s6-overlay. The standalone one works; the base images are the convention and bring the supervisor
  integration for free.

**Acceptance**
- [x] The image is published for `linux/amd64` and `linux/arm64` and starts on both. Done in
      Phase 2c: `build-docker` matrix on native `ubuntu-latest`/`ubuntu-24.04-arm` runners,
      `merge-manifest` job combining both by digest. Both matrix legs confirmed passing on real
      native runners on PR #566's CI run (29s each, no QEMU). The "published" half — the manifest
      actually pushed to `ghcr`/Docker Hub — still needs a push-to-`main` or release event, since
      `merge-manifest` only runs when `should_publish` is true and a pull request never sets it.
- [ ] The add-on installs on HAOS from the repository, appears in the sidebar, and the UI is fully
      usable through Ingress — including deep links and page reloads.
- [ ] A request that sets the ingress header but does not come from the Supervisor is rejected.
- [ ] Add-on restart and add-on update preserve brains, trained models and sessions.
- [ ] The armv7 limitation is documented where a user will see it before installing.

---

## 4. Cross-cutting concerns

**Testing.** Every phase from 3 onward is measured against the characterization suite from Phase 2.
Where a phase changes predictions on purpose, the baseline is regenerated deliberately and the pull
request says why — a deviation inside the tolerance is a reason to look, not a licence to proceed.
That lesson is written down in the pvlearn plan (chapter 6, addendum to point 6) and was learned the
hard way there.

**Documentation.** Phase 3c moves the user-facing documentation out of the README and into a
published MkDocs site. Diagrams are Mermaid, the convention `pvlearn` already standardises on and
the one that stays reviewable in a pull request; the single stale PlantUML model that used to sit
in `docs/diagrams/` was deleted rather than converted. Before the add-on ships, the site needs the
armv7 limitation and a description of what changes for existing users.

**Pydantic style.** Field definitions across the models use `Field(None, example=...)`. `example` is
the Pydantic v1 spelling, and `Field(None, ...)` gives a required-looking field a `None` default.
Both degrade the generated OpenAPI schema. Worth a sweep, most naturally during Phase 1.

**Versioning.** SemVer. Phase 5 (persistence), Phase 7 (encoding) and Phase 8 (estimator) each
invalidate trained models and each need an explicit changelog entry saying so.

---

## 5. Open decisions

1. **Model artifacts in SQLite or on disk?** Training data, configuration and keys clearly belong in
   the database. Pickled models are a different matter — as BLOBs everything sits in one file and
   backups are trivial; as files they stay inspectable and the database stays small. Decide in
   Phase 5.
2. **Migration tooling.** A `PRAGMA user_version` counter with hand-written migration steps, or
   SQLAlchemy/Alembic. The project has no ORM today and adding one for four tables is a large
   dependency for little gain — but hand-written migrations need discipline. Decide in Phase 5.
3. **Fate of `estimators` and `max_depth`** in `BrainEstimatorConfiguration` once the estimator
   changes. Decide in Phase 8.
4. **Coverage target.** `pvlearn` gates at 90%. ~~Where this project starts and how fast it
   ratchets needs a number per phase, not a wish.~~ Resolved in Phase 2: `fail_under = 85` in
   `core/pyproject.toml`'s `[tool.coverage.report]`, the characterization suite's actual combined
   line+branch coverage (85.75% measured, rounded down for margin). CI's existing
   `pytest --cov=learninghouse --cov-report=xml:coverage.xml` step in `build_project.yml` enforces
   it automatically - pytest-cov reads `fail_under` from the coverage config, no separate CI change
   needed. Next ratchet point is Phase 3: each dependency-update pull request that adds coverage
   should raise the floor to match, rather than leaving it at the Phase 2 number indefinitely.
5. **Home Assistant base image versus standalone Dockerfile** for the add-on. Decide in Phase 9.
6. **Shuffled `train_test_split`** in `prepare_training`. For genuinely independent observations it
   is correct; for timestamped, autocorrelated rows it is not. The same question is open in pvlearn.
   Whether learninghouse switches to a chronological split — and whether that is per brain or
   global — is a real modelling decision, not a bug fix.
7. ~~**`LEARNINGHOUSE_*` environment variables: deprecated fallback or breaking change** once
   `configuration.yaml` / `secrets.yaml` land.~~ Resolved in Phase 3b: breaking change, mitigated by
   a one-shot migration script (`learninghouse-migrate-config`) documented in the README for both
   console and Docker use — no permanent env-var fallback.

---

## 6. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Phases 5, 7 and 8 change predictions unnoticed | Silent quality loss in users' installations | Phase 2 first; every later phase measured against its baseline |
| Phase 2 gets cut short under time pressure | Every subsequent phase becomes unverifiable | The pvlearn plan made the same call in the opposite direction and it paid off — see its Phase 0 |
| scikit-learn 1.9.0 bump invalidates existing brains without the version check catching it | Models keep loading and silently mispredict | Verify `BrainNotActual` covers the library version before Phase 3 merges |
| Exact pins in pvlearn collide with learninghouse's own | Installation fails outright | Align shared pins in Phase 3, before pvlearn is added in Phase 6 |
| Ingress header trusted without checking the peer | Complete authentication bypass over the exposed port | Verify the Supervisor's address; covered by an explicit acceptance criterion in Phase 9 |
| Existing deployments break silently when `LEARNINGHOUSE_*` env vars stop being read | Users lose their configuration on upgrade | Phase 3b ships a one-shot migration script plus README/changelog documentation, required by its acceptance criteria |
| The plan grows to absorb the pvlearn integration | Nothing ships | Scheduler, event bus, weather providers and API changes are explicitly out of scope and get their own plan |

---

## 7. Critical path

```
P1  Toolchain + CI gates            ← commands must exist before they are documented
 │
P2  Tests + de-globalization        ← without this nothing below is verifiable
 │
P2b Angular test foundation         ← same reasoning as P2, applied before P3 touches the UI stack
 │
P2c uv build + Docker + CI caching  ← pins land in a lockfile once, not pip then uv
 │
P3  Dependency updates              ← aligns shared pins with pvlearn
 │
P3b Config via YAML + secrets       ← gives Phase 4's jwt_secret a home before Phase 4 needs it
 │
P3c Documentation site              ← split the README before four more phases add pages to it
 │
P4  Security hardening              ← cheaper now than after the add-on ships
 │
P5  SQLite persistence              ← time-series-shaped schema, ingest split from training
 │
P6  pvlearn as a dependency         ← dependency only, no behaviour
 │
P7  Sensor types via pvlearn encoders
 │
P8  Brain on a pipeline + HistGradientBoosting
 │
P9  Home Assistant add-on
```

The three hardest things to revise later, and therefore the ones deserving the most care: the
**SQLite schema** (Phase 5), because live data has to be migrated once brains exist in the field;
the **feature encoding** (Phase 7), because it invalidates every trained model; and the **Ingress
authentication rule** (Phase 9), because getting it wrong is a bypass rather than a bug.

What comes after this plan — scheduled weather retrieval, an event bus if one proves necessary, the
API changes for horizon forecasts, and the PV brain type itself — is deliberately left to a separate
plan, written once this foundation is in place.
