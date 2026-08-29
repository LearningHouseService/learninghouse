# 8. Code carries no comments; the reasoning lives here

- **Status:** accepted
- **Date:** 2026-08-29

## Context

The codebase explained itself in two places at once. Some reasoning sat in this decision series,
some in comments above the code it described - the bootstrap rule for `config_directory`, why the
auth dependencies stopped being bound methods of a singleton, why the brain cache is keyed by
directory and name. Both kinds of text made claims about the code.

Only one of them is checked. A comment is copied along when code moves, survives the change that
made it wrong, and is read as current at the moment it is most misleading. Nothing fails when it
goes stale. A decision record is dated, append-only, reviewed as a document, and says what was
true when it was written - which is what a reader needs from it.

The comments also encouraged writing prose instead of code: an explanation above a block is
cheaper than the constant, the named function or the type that would have made the block obvious.

## Decision

- **No comments in source files.** Naming does the explaining: a named constant instead of a
  literal, a named function instead of a commented block, a type instead of a sentence about what
  a value is.
- **Machine-read directives stay**, because they are not prose: `# pragma: no cover`,
  `# type: ignore`, `# pyright: ignore`, linter pragmas.
- **Reasoning goes into this series.** Why one approach was chosen over another, what a trade-off
  cost, which condition an implementation depends on - all of it is an ADR. Feeling the need to
  explain something while writing code is the signal to write or extend a record here.
- **The same applies to project configuration** - `pyproject.toml`, `.github/`, build and CI
  files. A pin, a coverage floor or a Dependabot group is a decision like any other, and its
  reasoning drifts from the value the same way.
- **Test modules are exempt.** Their docstrings describe what the suite pins, which is the
  specification of the tests rather than a claim about production code, and the characterization
  suite is only useful while a reader can tell deliberate behaviour from accident.
- **Files that are themselves user documentation are exempt**, because their comments are the
  documentation rather than a note about it: `configuration.yaml.example` and the
  `configuration.yaml` baked into the Docker image explain every setting to the person editing
  them.

Rejected alternative: keep comments for "small" explanations and use records only for larger
decisions. That is the state this replaces - the boundary is not decidable while writing, so both
places fill up and neither is complete.

## Consequence

The comments that existed were removed in the same change. Everything they carried that was not
already recorded is written below, so that removing them cost no information.

A reader who wants to know why a piece of code looks the way it does now has exactly one place to
look, and that place is versioned as documentation rather than as a byproduct of the line it sat
above.

## Reasoning rescued from the comments this removed

- **`SECRET_FIELDS` (`core/settings/models.py`) is shared with `learninghouse.scripts.migrate_config`.**
  Those fields must never be readable from `configuration.yaml`, the environment or the log. One
  shared definition is what keeps the settings loader and the migration script from drifting apart
  on what counts as sensitive.
- **`config_directory` is a bootstrap value, not migrated content.** It says where the
  `configuration.yaml` / `secrets.yaml` pair lives, so it cannot also be a key inside them - in the
  loader and in the migration script alike.
- **The migration script reads `.env` first and lets the environment override it**, matching the
  precedence of the settings loader it replaces (environment read before dotenv, first write wins).
- **The auth dependencies are free functions, not bound methods.** They used to be methods of a
  module-level `authservice` singleton, attached to routers at import time, which permanently bound
  every router to whichever instance happened to exist when the module was first imported. Resolved
  through `Depends(auth_service_cached)`, the service is looked up per request.
- **The protected auth routes are registered unconditionally.** `EnforceInitialPasswordChange`
  already blocks every endpoint outside its allow-list while the administration password is the
  initial one. Gating the *registration* on that same flag meant the routes stayed `404` for the
  rest of the process once a single request had seen an initial password - changing the password
  did not bring them back without a restart.
- **`BrainService.brains` is keyed by `(brains_directory, name)`, not by name.** Two brains
  directories in one process - which the test suite does deliberately - can hold a brain of the
  same name, and a name-only key would serve the wrong one.
- **`BrainService`'s "no dependent value" branch is unreachable today.** The API layer rejects such
  a training request before it gets there; the branch is kept because the service is also called
  directly.
- **Two pyright workarounds in `core/logger`.** `LOGURU_FORMAT` is typed as the union of everything
  loguru's environment parser can return, though it is always the default format string here; and
  loguru types its handler dictionaries as TypedDicts whose `format` key rejects a callable, which
  the runtime accepts.
- **`ListModel.__iter__` deliberately overrides pydantic's.** Iterating the wrapped list instead of
  `(field, value)` tuples is the entire purpose of that wrapper.
- **The service version comes from package metadata** written by `setuptools-scm` at build time;
  the fallback exists only for a source tree that was never installed.
- **`[tool.setuptools_scm] root = ".."`.** The git repository is the monorepo root, one level above
  `core/`, so the version comes from tags on that repository rather than from this directory.
- **`namespaces = true` in the package find.** It is what picks up `learninghouse/static` and the
  `learninghouse/ui` tree, neither of which carries an `__init__.py`. The UI is built separately and
  copied in before the wheel is built, so the find has to tolerate both its presence in CI and its
  absence in a plain checkout.
- **The coverage floor is the suite's own measured coverage**, rounded down for a small margin: 85
  when the characterization suite was written, 87 with the `configuration.yaml` / `secrets.yaml`
  loader and the migration script tests, 88 with the CORS, API key, hashing and secret-logging
  tests. Work that adds coverage raises it to match rather than leaving the slack behind; pytest-cov
  reads `fail_under` in CI, so no separate CI change is needed.
- **The `argon2-cffi-bindings` pin** is explained in
  [0006](0006-argon2id-passwords-and-hashed-api-keys.md), the exact-pin rules and the `scipy` /
  `joblib` declarations in [0003](0003-exact-pins-shared-with-pvlearn.md), and the Dependabot
  `angular` group in [0004](0004-dependabot-groups-for-framework-majors.md) - those comments
  duplicated records that already existed, which is the other half of why they went.
