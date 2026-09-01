# Architecture Decisions

Records of decisions that shaped the project, written when the decision was made and kept
afterwards. They explain why something is the way it is, which the code itself cannot.

They are numbered sequentially and append-only. A decision that no longer holds is not edited or
deleted, it is superseded by a later one that says so.

| # | Decision | Status | In short |
|---|---|---|---|
| [0001](0001-uv-for-the-python-build.md) | uv for the Python build and the Docker image | Accepted | Dependencies resolve through a committed `uv.lock`; the Docker image syncs that lockfile and installs the built wheel on top, and `piwheels` is gone with `armv7`. |
| [0002](0002-yaml-configuration-with-a-one-shot-migration.md) | YAML configuration with a one-shot migration | Accepted | `configuration.yaml` and `secrets.yaml` replace the `LEARNINGHOUSE_*` variables outright; a script migrates once instead of a permanent fallback. |
| [0003](0003-exact-pins-shared-with-pvlearn.md) | Shared dependencies are pinned exactly, to pvlearn's values | Accepted | `numpy`, `pandas`, `scipy`, `scikit-learn`, `pydantic` and `joblib` match pvlearn's pins, so depending on pvlearn stays a one-line change. |
| [0004](0004-dependabot-groups-for-framework-majors.md) | Dependabot groups the Angular ecosystem, and does not own framework majors | Accepted | Angular's packages ship as one grouped pull request; a framework major is done by hand with migration schematics, not by a version bump. |
| [0005](0005-the-documentation-site.md) | The documentation site is built from `core/`, and published on release only | Accepted | MkDocs Material builds from `docs/` with the docs dependencies in `core/`'s lockfile; a dead link fails the build, and Pages deploys after the release it documents. |
| [0006](0006-argon2id-passwords-and-hashed-api-keys.md) | Argon2id for the password, a salted SHA-256 for API keys | Accepted | `passlib` is unmaintained and its cost was being paid per request on keys that never needed it; the old format is not read and nothing migrates it — the persistence release starts the security store empty. |
| [0007](0007-no-comments-in-code.md) | Code carries no comments; the reasoning lives here | Accepted | A comment survives the code it described and then misleads; naming explains the code, this series explains the choices. |

## Writing a new one

Take the next free number, keep the file name in the `NNNN-kebab-case-title.md` shape, and add a
row to the table above. State the context, the decision, and the consequence you accepted. A
decision that only records what was done, without the alternatives that were rejected, is not
worth keeping.
