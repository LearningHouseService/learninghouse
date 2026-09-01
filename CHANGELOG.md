# Changelog

Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The reasoning
behind the larger entries lives in [docs/decisions/](docs/decisions/index.md).

## Unreleased

### Security

- **Cross-origin requests are restricted to configured origins.** The service used to send
  `Access-Control-Allow-Origin` for every origin while also allowing credentials, which Starlette
  resolves by reflecting whatever `Origin` a request carried - so any page a user visited could
  call their instance with their session. `cors_allowed_origins` in `configuration.yaml` now names
  the origins that may. The service's own origin is always allowed - that is where the UI is
  served from, so nothing has to be configured for it - and `*` is refused at startup.
- **API keys are no longer accepted from the query string.** `?api_key=` returns `403`
  `APIKEY_IN_QUERY`; send the key as the `X-LEARNINGHOUSE-API-KEY` header. Query strings are
  written to access logs, proxy logs and browser history. `allow_api_key_query: true` re-enables
  the old behaviour for as long as it takes to migrate a client, and logs a warning on every
  request accepted that way.
- **The administration password is hashed with argon2id** instead of `passlib`'s `sha512_crypt`,
  and API keys with a salted SHA-256. An API key is no longer verified through several hundred
  thousand hash rounds on every prediction request. See "Changed (breaking)" for what this costs on
  upgrade.
- **A rejected API key and a rejected administration login are logged** as a warning naming
  neither value, so repeated attempts against an instance are visible. Guessing is bounded by the
  request rate, not by the hash.
- An invalid configuration now ends in a readable message and exit code `1` rather than a pydantic
  traceback.
- A start that has to generate `jwt_secret` says so in the log, naming the file it wrote and not
  the secret.

### Fixed

- Opening the service's root URL while the administration password is still the fallback one now
  redirects to the UI instead of answering `401`. The redirect was blocked by the gate that
  deactivates every other endpoint until the password is changed, so a fresh installation had to be
  sent to `/ui` by hand.

### Changed (breaking)

- **Credentials from an earlier release are not carried over.** `sha512_crypt` hashes are not read
  any more, and nothing migrates them: the administration account is back on the fallback password
  `learninghouse`, with the initial-password gate armed, and there are no API keys. Log in, set a
  new password, create the keys again and update your clients. Verifying the old hashes instead
  would have kept the unmaintained `passlib` in the dependency list indefinitely, since nothing
  forces an installation to log in again; see
  [decision 0006](https://learninghouseservice.github.io/learninghouse/decisions/0006-argon2id-passwords-and-hashed-api-keys/).
- `/api/versions` reports `argon2` where it used to report `passlib`.
- **Configuration moved from `LEARNINGHOUSE_*` environment variables to `configuration.yaml` /
  `secrets.yaml`** inside the config directory. Only `LEARNINGHOUSE_CONFIG_DIRECTORY` (where those
  two files live) is still read from the environment. Run `learninghouse-migrate-config` once
  against your existing config directory (console) or mounted volume (Docker) before upgrading -
  see the documentation site's
  [Migration](https://learninghouseservice.github.io/learninghouse/migration/environment-variables/)
  page. The script only migrates settings, never brain data, sensors, or the security database.
- `jwt_secret` now persists in `secrets.yaml`, generated once on first start instead of being
  regenerated on every process start - existing sessions no longer get invalidated by a restart.
- **Brains trained before this release have to be retrained.** `scikit-learn` moved from 1.8.0 to
  1.9.0 (aligned with `pvlearn`'s pins), and a brain records the library versions it was trained
  with. One trained under 1.8.0 is now rejected rather than loaded best-effort, because a model
  read back by a different estimator release can silently mispredict. The training data is
  untouched, so a `POST` to `/api/brain/:name/training` retrains without resending anything.

### Added

- **A documentation site**, built from `docs/` with MkDocs Material and published to
  <https://learninghouseservice.github.io/learninghouse/> on release. Everything that used to sit
  in the README - configuration keys, sensors, brains, security, training, prediction, Docker, the
  migration instructions - now has its own page, plus a troubleshooting page and an append-only
  series of architecture decision records under
  [Reference](https://learninghouseservice.github.io/learninghouse/decisions/).
- CI builds the site with `mkdocs build --strict` on every push and pull request and uploads it as
  an artifact, so a documentation change can be reviewed as a browsable site. A dead internal
  link, an unknown anchor or a nav entry pointing at a missing file fails the build.

### Changed

- The README is reduced to the overview, the feature list, a quick start and a link to the
  documentation site.
