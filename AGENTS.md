# learninghouse — Agent & AI Instructions

This file is the single source of truth for AI coding assistants (Claude Code, GitHub Copilot,
Cursor, etc.). Tool-specific configurations reference this file and add only tool-specific syntax
on top.

The authoritative roadmap and the architecture decisions that go with it live in
[`docs/modernization-plan.md`](docs/modernization-plan.md). Read it before starting any
non-trivial task — it defines which phase the project is in and which changes are in scope. The
plan deliberately stops before the `pvlearn` integration; scheduler, event bus, weather providers
and the API changes they need get their own plan.

## Project Overview

- **Purpose:** REST service that learns a household's own behaviour ("brains") from pushed sensor
  data and predicts values from it — darkness detection, heating setpoints, and anything else a
  user configures.
- **Languages:** Python (>=3.13, <4) for the service, TypeScript/Angular for the UI.
- **Package managers:** [uv](https://docs.astral.sh/uv/) with `pyproject.toml` / `uv.lock` (`core/`), npm (`ui/`).
- **Related project:** [`pvlearn`](https://github.com/LearningHouseService/pvlearn) — the PV
  forecast library learninghouse will depend on from Phase 6 onwards. Shared dependency pins are
  aligned with it; see chapter 3 of the modernization plan.

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
docs/                       # documentation and the modernization plan
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

CI runs `ruff check`, `ruff format --check`, `pyright` and `pytest` on every push and pull
request, before the UI and the wheel are built.

### Commits and pull requests

This repository uses the Developer Certificate of Origin, as `pvlearn` does. Every commit needs a
`Signed-off-by` trailer — commit with `git commit -s`. To repair a branch where it is missing:
`git rebase <base> --signoff` followed by `git push --force-with-lease`.

**One pull request per phase of the modernization plan, not per commit.** A phase lands as a
single branch with however many commits it takes, reviewed and merged as one unit. Commits within
a branch stay individually meaningful. Merges are squashed, so the pull request description
carries the reasoning that survives into `main`'s history.

---

## Code Conventions

- Python >=3.13 syntax and language features.
- All code comments and documentation in **English**, independent of the language used in
  planning documents or in the conversation.
- Type hints are mandatory on public functions and methods; `pyright` runs in CI and the codebase
  is currently free of type errors — keep it that way rather than adding ignores.
- Pydantic models for everything crossing a boundary (configuration, API payloads, persisted
  data).
- Pydantic fields: `Field(..., examples=[...])` for required fields and
  `Field(default=..., examples=[...])` for optional ones. Never `Field(None, example=...)` — the
  singular `example` is pydantic v1 and a positional default is not recognized by pyright, which
  is how the whole codebase ended up claiming fields were optional when they are not.
- For diagrams use Mermaid.

### Project Patterns

- **Nothing may be process-global.** Settings, the auth service and brain paths are being moved
  to dependencies passed in or resolved per request (Phase 2). New code must not add another
  module-level `settings = service_settings()` or another singleton — this is the coupling that
  makes the service hard to test and impossible to run with more than one worker.
- **Model persistence:** joblib pickles with version metadata. A model whose service or
  scikit-learn version does not match the running one is rejected and retrained, never loaded
  best-effort.
- **Errors:** raise a `LearningHouseException` subclass from `errors/`; each one carries its
  status code and its OpenAPI description, so a new error type documents itself. `errors/` is a
  standalone top-level module with no dependency on `api`, `models` or `services` — it existed as
  `api/errors/` until Phase 2 of the modernization plan, where models and services importing from
  inside the `api` package created a circular import depending on which module happened to be
  imported first.

### Testing

- Test files mirror the source structure under `core/tests/`.
- `pytest` with fixtures in `core/tests/conftest.py`.
- Test classes prefixed with `Test`, methods with `test_`.
- Tests run offline and write nothing outside `tmp_path` — no writes into the repository, no
  network access.
- Phase 2 introduces the characterization suite and a coverage floor; until then the suite is a
  smoke test and the floor is not yet enforced.

---

## Security Guidelines

- Never commit secrets or credentials.
- Validate all external input through pydantic models.
- Filter sensitive data (API keys, tokens, passwords) from log output.
- The known open issues — wildcard CORS with credentials, API keys accepted in the query string,
  a JWT secret regenerated on every start — are Phase 4 of the modernization plan. Do not build
  new behaviour that depends on them.
