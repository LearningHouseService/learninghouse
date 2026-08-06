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
| 3 | Dependency updates | your list #2 |
| 4 | Security hardening | added in review |
| 5 | Persistence on SQLite | your list #3 |
| 6 | pvlearn as a library dependency | your list #4 |
| 7 | Sensor types from the pvlearn encoders | your list #5 |
| 8 | Brain on a scikit-learn pipeline | your list #6 |
| 9 | Home Assistant add-on | from the add-on assessment |

Phases 2 and 4 did not come from the original list; they were added during review and confirmed.
The reasoning for each is in its own section.

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
- [ ] Every `/api` route has at least one test covering the success path and one covering its
      documented error.
- [ ] Training and prediction on the fixture dataset are pinned by a test that would fail if the
      predicted values changed.
- [ ] Two tests in the same session can use two different brains directories.
- [ ] `pytest` runs offline, with no writes outside `tmp_path`.
- [ ] A coverage floor is configured in CI and is met.

---

### Phase 3 — Dependency updates

**Goal:** Current, coherent dependency set on both sides, with the shared packages already aligned
to what `pvlearn` pins.

- Merge or close the open Dependabot branches (currently nine, spanning GitHub Actions, npm and
  pip).
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

### Phase 4 — Security hardening

**Goal:** Close the findings that would otherwise ship into people's homes in Phase 9.

These are small, independent changes, and each of them is harder to make after the add-on exists,
because by then someone is depending on the current behaviour.

- **CORS.** `service.py:52` sets `allow_origins=["*"]` together with `allow_credentials=True`.
  Starlette resolves that combination by reflecting the request's `Origin` header back instead of
  sending a wildcard, which means any web page a user visits can make authenticated requests to
  their learninghouse instance. Replace with a configurable origin list, defaulting to the UI's own
  origin.
- **API keys in the query string.** `services/auth.py:32` accepts the key via `APIKeyQuery` as well
  as the header. Query strings end up in access logs, proxy logs and browser history. Deprecate the
  query variant, keep the header.
- **JWT secret.** `core/settings/models.py:39` defaults `jwt_secret` to a fresh `token_hex(16)` per
  process start. Consequences: every restart invalidates all sessions, and with `workers > 1` each
  worker generates its own secret, so tokens issued by one worker are rejected by another. Persist
  the secret (Phase 5 gives it a natural home) and log a warning when it had to be generated.
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

- Single SQLite database in the configuration directory. Tables for brains, sensors, training data,
  security/API keys, and the JWT secret from Phase 4.
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

**Multi-architecture build.** `build_project.yml:164` sets `platforms: all` on the QEMU setup step,
but `docker/build-push-action` receives no `platforms` input — so QEMU and Buildx are configured and
then not used, and the published image is `amd64` only. Add `platforms: linux/amd64,linux/arm64`.
`armv7` stays unsupported, consistent with the pvlearn plan, which excludes it because of the
numpy/scipy/scikit-learn wheel situation. That limitation belongs prominently in the documentation.

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
  with `LEARNINGHOUSE_CONFIG_DIRECTORY` pointed at `/data`.
- A watchdog URL. `/api/mode` exists and would serve, though a dedicated `/health` that does not
  touch auth state is cleaner.
- Decide between the current standalone Dockerfile and the Home Assistant Python base images with
  s6-overlay. The standalone one works; the base images are the convention and bring the supervisor
  integration for free.

**Acceptance**
- [ ] The image is published for `linux/amd64` and `linux/arm64` and starts on both.
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
4. **Coverage target.** `pvlearn` gates at 90%. Where this project starts and how fast it ratchets
   needs a number per phase, not a wish.
5. **Home Assistant base image versus standalone Dockerfile** for the add-on. Decide in Phase 9.
6. **Shuffled `train_test_split`** in `prepare_training`. For genuinely independent observations it
   is correct; for timestamped, autocorrelated rows it is not. The same question is open in pvlearn.
   Whether learninghouse switches to a chronological split — and whether that is per brain or
   global — is a real modelling decision, not a bug fix.

---

## 6. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Phases 5, 7 and 8 change predictions unnoticed | Silent quality loss in users' installations | Phase 2 first; every later phase measured against its baseline |
| Phase 2 gets cut short under time pressure | Every subsequent phase becomes unverifiable | The pvlearn plan made the same call in the opposite direction and it paid off — see its Phase 0 |
| scikit-learn 1.9.0 bump invalidates existing brains without the version check catching it | Models keep loading and silently mispredict | Verify `BrainNotActual` covers the library version before Phase 3 merges |
| Exact pins in pvlearn collide with learninghouse's own | Installation fails outright | Align shared pins in Phase 3, before pvlearn is added in Phase 6 |
| Ingress header trusted without checking the peer | Complete authentication bypass over the exposed port | Verify the Supervisor's address; covered by an explicit acceptance criterion in Phase 9 |
| The plan grows to absorb the pvlearn integration | Nothing ships | Scheduler, event bus, weather providers and API changes are explicitly out of scope and get their own plan |

---

## 7. Critical path

```
P1  Toolchain + CI gates            ← commands must exist before they are documented
 │
P2  Tests + de-globalization        ← without this nothing below is verifiable
 │
P3  Dependency updates              ← aligns shared pins with pvlearn
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
