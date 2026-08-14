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
| 4 | Security hardening | added in review |
| 5 | Persistence on SQLite | your list #3 |
| 6 | pvlearn as a library dependency | your list #4 |
| 7 | Sensor types from the pvlearn encoders | your list #5 |
| 8 | Brain on a scikit-learn pipeline | your list #6 |
| 9 | Home Assistant add-on | from the add-on assessment |

Phases 2, 2b, 2c, 3b and 4 did not come from the original list; they were added during review and
confirmed. The reasoning for each is in its own section.

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
- [ ] CI's `check-core` and `build-core` jobs use `astral-sh/setup-uv` with caching enabled, and a
      second run against an unchanged lockfile is measurably faster than the pip-cache baseline.
      Jobs are wired up (`astral-sh/setup-uv@v10`, `enable-cache: true`,
      `cache-dependency-glob: "core/uv.lock"`); the speed comparison itself needs an actual run on
      GitHub Actions and could not be verified locally — check after this branch's first CI run.
- [x] The Docker image builds via `uv` and starts identically to the pip-built image (same
      `/api/versions` output, same entry point). Verified locally against the final two-layer
      buildimage (lockfile sync, then wheel installed with `--no-deps`, `piwheels` dropped): built,
      ran it, `curl /api/versions` returned the same payload the pip-built image returned, same
      `python3 -m learninghouse` entry point, same startup log lines.
- [x] `uv.lock` is committed and CI fails if it is out of sync with `pyproject.toml`. `check-core`
      runs `uv sync --extra dev --locked`; verified locally that `--locked` accepts a matching
      lockfile and rejects one made stale by editing a pin in `pyproject.toml` without updating it.
- [x] The `arm64` leg of the Docker build resolves and installs every dependency from
      `manylinux_aarch64` wheels, nothing compiles from source. Verified locally: `docker buildx
      build --platform linux/arm64` against the same `Dockerfile` (QEMU-emulated, since this
      machine is `amd64`) completed the dependency-sync and wheel-install layers successfully; the
      real native-runner (`ubuntu-24.04-arm`) build and the multi-arch manifest push itself still
      need this branch's first CI run to confirm, same open item as the CI-cache-speed criterion
      above.

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
- Angular and the npm toolchain to current.
- Python dependencies to current — **with one constraint that shapes this phase**: `pvlearn` pins
  its dependencies *exactly*, not as ranges. Once Phase 6 adds `pvlearn` to `install_requires`, pip
  will refuse any different pin of a shared package. In practice learninghouse inherits pvlearn's
  pins for `numpy`, `pandas`, `scipy`, `scikit-learn`, `pydantic` and `joblib`. Aligning them here
  keeps Phase 6 a one-line change instead of a resolution fight.

  | Package | learninghouse today | pvlearn pin |
  |---|---|---|
  | `numpy` | 2.4.4 | 2.5.1 |
  | `pandas` | 3.0.3 | 3.0.5 |
  | `scipy` | — | 1.18.0 |
  | `scikit-learn` | 1.8.0 | 1.9.0 |
  | `pydantic` | 2.13.4 | 2.13.4 ✓ |

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
- [ ] Dependabot backlog is empty.
- [ ] The characterization suite from Phase 2 passes unchanged, or every deviation is explained and
      the baseline deliberately regenerated.
- [ ] Shared pins match `pvlearn` exactly, verified by installing both into one environment.
- [ ] A brain trained before the update is either loaded correctly or rejected with a clear message
      and retrained — never loaded best-effort.
- [ ] The UI builds and its Karma suite passes.

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
- [ ] Every setting currently readable from a `LEARNINGHOUSE_*` environment variable is readable from
      `configuration.yaml`.
- [ ] `jwt_secret` (and any other sensitive value) is read only from `secrets.yaml`, never from
      `configuration.yaml`, the environment, or logged output.
- [ ] `jwt_secret` persists across a service restart without depending on Phase 5.
- [ ] The Docker image starts correctly with only a mounted `configuration.yaml`, no `LEARNINGHOUSE_*`
      environment variables set.
- [ ] The migration script converts a representative set of `LEARNINGHOUSE_*` variables (including at
      least one that must land in `secrets.yaml`) into a correct `configuration.yaml` /
      `secrets.yaml` pair, verified against a fixture of the old environment-variable layout.
- [ ] The migration script refuses to overwrite existing YAML files without `--force`.
- [ ] README documents console and Docker invocation of the migration script, and the changelog
      records the breaking change.

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
- Password hashing per Phase 3, if not already taken there.

**Acceptance**
- [ ] A cross-origin credentialed request from an origin that is not configured is rejected.
- [ ] Sessions survive a service restart.
- [ ] `workers > 1` either works correctly or is rejected at startup with an explanation.
- [ ] No secret, token or API key appears in log output at any level.

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

**Acceptance**
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
      `merge-manifest` job pushing the combined manifest. Verified locally for `arm64` via
      QEMU-emulated `docker buildx build --platform linux/arm64` — dependency resolution and image
      build succeed (`manylinux_aarch64` wheels throughout, nothing compiles); real native-runner
      confirmation happens on this branch's first CI run, same as the CI-cache-speed criterion in
      Phase 2c.
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

**Documentation.** Currently `docs/` holds one PlantUML diagram. `pvlearn` standardises on Mermaid;
adopting that here keeps diagrams reviewable in a pull request. Before the add-on ships, the README
needs the armv7 limitation and a description of what changes for existing users.

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
