# learninghouse — Agent & AI Instructions

This file is the single source of truth for AI coding assistants (Claude Code, GitHub Copilot,
Cursor, etc.). Tool-specific configurations reference this file and add only tool-specific syntax
on top.

The decisions that shaped the code, and the reasoning that the code itself cannot carry, live in
[`docs/decisions/`](docs/decisions/index.md) as numbered, append-only records. Read the ones that
touch what you are about to change — they are the durable half of the reasoning; working notes and
roadmaps are not.

## Project Overview

- **Purpose:** REST service that learns a household's own behaviour ("brains") from pushed sensor
  data and predicts values from it — darkness detection, heating setpoints, and anything else a
  user configures.
- **Languages:** Python (>=3.13, <4) for the service, TypeScript/Angular for the UI.
- **Package managers:** [uv](https://docs.astral.sh/uv/) with `pyproject.toml` / `uv.lock` (`core/`), npm (`ui/`).
- **Related project:** [`pvlearn`](https://github.com/LearningHouseService/pvlearn) — the PV
  forecast library learninghouse is going to depend on. It pins its dependencies *exactly*, so the
  packages both sides share (`numpy`, `pandas`, `scipy`, `scikit-learn`, `pydantic`, `joblib`) are
  pinned here to the same versions; bumping one of them means checking pvlearn's `pyproject.toml`
  in the same breath. See
  [decision 0003](docs/decisions/0003-exact-pins-shared-with-pvlearn.md).

### Directory Structure

```
core/                       # the Python service — everything installable lives here
├── learninghouse/
│   ├── api/                # FastAPI routers and middleware
│   ├── core/               # settings and logging infrastructure
│   ├── errors/             # LearningHouseException subclasses and their OpenAPI shape
│   ├── models/             # pydantic models and the brain/dataset domain objects
│   ├── scripts/            # console-script entry points shipped with the package
│   │                       # (e.g. learninghouse-migrate-config)
│   ├── services/           # brain training and prediction, sensors, auth
│   ├── static/             # swagger assets served by the service
│   └── ui/                 # built Angular UI, copied in by CI — not in git
├── tests/                  # pytest suite mirroring the learninghouse/ structure
├── scripts/                # one-off maintenance scripts, not shipped with the package
└── pyproject.toml          # packaging, dependency pins and tool configuration
ui/                         # Angular frontend
docker/                     # Dockerfile; the image installs the wheel, it has no source tree
docs/                       # the MkDocs site sources (mkdocs.yml is at the repository root)
└── decisions/              # numbered, append-only architecture decision records
```

`core/README.md`, `core/LICENSE` and `core/THIRD-PARTY-NOTICES` are symlinks to the files at the
repository root, so that `uv sync` works from a plain checkout without a copy step.

### Versioning

The version comes from git tags via `setuptools-scm` and is read back at runtime through
`importlib.metadata`. There is no version file to edit and none to commit. A build from a shallow
clone without tags produces a fallback version, which is why CI checks out with `fetch-depth: 0`.

---

## Developer Commands

All Python commands run in `core/`:

```bash
# Install with all development dependencies (creates core/.venv, writes/reads uv.lock)
uv sync --extra dev

# Lint and format (must pass before commit)
uv run ruff check .
uv run ruff check . --fix    # auto-fix
uv run ruff format .

# Type check — resolves against core/.venv, which uv sync created
uv run pyright

# Tests (parallel via pytest-xdist, -v --tb=short set in pyproject.toml)
uv run pytest
uv run pytest --cov=learninghouse --cov-report=xml:coverage.xml
uv run pytest tests/path/to/test_file.py
```

UI commands run in `ui/`: `npm install`, `npm run build:core`, `npm test`.

Documentation commands also run in `core/`, even though `mkdocs.yml` sits at the repository root
— the documentation dependencies are the `docs` extra of `core/pyproject.toml`, locked in
`core/uv.lock`, because this is the only Python project in the repository:

```bash
uv sync --extra docs
uv run mkdocs build --strict --config-file ../mkdocs.yml   # writes site/ at the repo root
uv run mkdocs serve --config-file ../mkdocs.yml            # live preview on :8000
```

CI runs `ruff check`, `ruff format --check`, `pyright` and `pytest` on every push and pull
request, before the UI and the wheel are built. `mkdocs build --strict` runs alongside them and
uploads the rendered site as an artifact; the site is published to GitHub Pages on release only.

### Commits and pull requests

This repository uses the Developer Certificate of Origin, as `pvlearn` does. Every commit needs a
`Signed-off-by` trailer — commit with `git commit -s`. To repair a branch where it is missing:
`git rebase <base> --signoff` followed by `git push --force-with-lease`.

**One pull request per coherent piece of work, not per commit.** Such a unit lands as a single
branch with however many commits it takes, reviewed and merged as one. Commits within a branch stay
individually meaningful. Merges are squashed, so the pull request description carries the reasoning
that survives into `main`'s history — and anything that outlives the pull request belongs in
`docs/decisions/`, not only in its description.

---

## Code Conventions

- Python >=3.13 syntax and language features.
- **Code carries no comments.** Naming is what explains it: a constant instead of a literal, a
  named function instead of a commented block. Only machine-read directives stay
  (`# pragma: no cover`, `# type: ignore`, `# pyright: ignore`, linter pragmas).
- **Reasoning lives in `docs/decisions/`, never in the source.** Why one approach was chosen over
  another, what a trade-off cost, which condition an implementation depends on — that is an ADR.
  A comment describing a decision outlives the code it described and then misleads; an ADR is
  dated and append-only, so it stays a record of a moment rather than a claim about current code.
  If an explanation feels necessary while writing code, write or extend the ADR instead.
- Documentation in **English**, independent of the language used in the conversation.
- Type hints are mandatory on public functions and methods; `pyright` runs in CI and the codebase
  is currently free of type errors — keep it that way rather than adding ignores.
- Pydantic models for everything crossing a boundary (configuration, API payloads, persisted
  data).
- Pydantic fields: `Field(..., examples=[...])` for required fields and
  `Field(default=..., examples=[...])` for optional ones. Never `Field(None, example=...)` — the
  singular `example` is pydantic v1 and a positional default is not recognized by pyright, which
  is how the whole codebase ended up claiming fields were optional when they are not.
- For diagrams use Mermaid.
- User-facing documentation lives in `docs/` and is published as a MkDocs Material site; the
  README carries only the overview, the feature list, a quick start and a link to the site. A new
  page needs a `nav` entry in `mkdocs.yml`, or the `--strict` build fails.
- Decisions that the code cannot explain by itself go into `docs/decisions/` as a numbered
  `NNNN-kebab-case-title.md`, with a row in `docs/decisions/index.md`. The series is append-only:
  a decision that no longer holds is superseded by a later one, never edited or deleted.

### Project Patterns

- **Nothing may be process-global.** Settings, the auth service and brain paths are resolved per
  request through FastAPI dependencies, not read at import time. New code must not add another
  module-level `settings = service_settings()` or another singleton — that coupling is what made
  the service hard to test and is why it cannot yet run with more than one worker (see
  [decision 0007](docs/decisions/0007-multi-worker-support-is-the-goal.md)).
- **Model persistence:** joblib pickles with version metadata. A model whose service or
  scikit-learn version does not match the running one is rejected and retrained, never loaded
  best-effort.
- **Errors:** raise a `LearningHouseException` subclass from `errors/`; each one carries its
  status code and its OpenAPI description, so a new error type documents itself. `errors/` is a
  standalone top-level module with no dependency on `api`, `models` or `services` — it was moved
  out of `api/errors/`, where models and services importing from inside the `api` package created a
  circular import depending on which module happened to be imported first. Do not move it back.

### Testing

- Test files mirror the source structure under `core/tests/`.
- `pytest` with fixtures in `core/tests/conftest.py`.
- Test classes prefixed with `Test`, methods with `test_`.
- Tests run offline and write nothing outside `tmp_path` — no writes into the repository, no
  network access.
- The suite is a **characterization suite**: it pins what the service does today, including
  behaviour nobody has decided to keep. A test that changes because production behaviour changed is
  a decision to take deliberately and to write down, not a test to adjust until it passes.
  `core/tests/test_baseline.py` pins a prediction on a fixed input; regenerate its baseline only on
  purpose, and say why in the pull request.
- A coverage floor is enforced through `fail_under` in `[tool.coverage.report]`
  (`core/pyproject.toml`), read by `pytest --cov` in CI. Work that adds coverage raises the floor to
  match rather than leaving slack behind; work that lowers it needs a reason in the pull request.

---

## Security Guidelines

- Never commit secrets or credentials.
- Validate all external input through pydantic models.
- Filter sensitive data (API keys, tokens, passwords) from log output.
- The hardening already in place, none of which may be weakened without a decision record:
  - **CORS** origins come from `cors_allowed_origins`; the service's own origin is always allowed
    and `*` is refused at startup, because a wildcard next to `allow_credentials=True` makes
    Starlette reflect the caller's own `Origin`.
  - **API keys** are read from the `X-LEARNINGHOUSE-API-KEY` header. The `?api_key=` query
    parameter is rejected unless `allow_api_key_query` is set for a migration, because query
    strings reach access logs, proxy logs and browser history.
  - **`jwt_secret`** persists in `secrets.yaml` (mode `0600`), generated once with a warning that
    names the file and never the value.
  - **`workers > 1` is refused at startup.** Interim guard while refresh tokens and the security
    database are per process — restoring multi-worker support is the goal, see
    [decision 0007](docs/decisions/0007-multi-worker-support-is-the-goal.md).
  - **Hashing** is argon2id for the administration password and a salted SHA-256 for API keys, see
    [decision 0006](docs/decisions/0006-argon2id-passwords-and-hashed-api-keys.md). The
    `sha512_crypt` format of earlier releases is not read at all: such a database has its password
    reset to the fallback and its API keys removed, once, on load. `passlib` is gone — do not
    reintroduce it.
  - **The API key hash choice depends on the key being generated here with full entropy.** A
    salted SHA-256 is right for 128 random bits and wrong for anything a client may choose, so
    client-supplied API keys would require changing the hash in the same breath.
    `tests/models/test_auth.py::TestApiKeyEntropy` guards that.
  - **A rejected credential is logged** (never its value) — guessing is bounded by the request
    rate, not by the hash. A rate limit for the authentication surface does not exist yet.
- Secrets never reach the log, at any level. `core/tests/test_secret_logging.py` pins this by
  running an administration flow with a DEBUG sink attached and searching the output.
