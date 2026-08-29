# Changelog

Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). See
[docs/modernization-plan.md](docs/modernization-plan.md) for the phased work behind these entries.

## Unreleased

### Changed (breaking)

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
