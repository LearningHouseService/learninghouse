# Changelog

Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). See
[docs/modernization-plan.md](docs/modernization-plan.md) for the phased work behind these entries.

## Unreleased

### Changed (breaking)

- **Configuration moved from `LEARNINGHOUSE_*` environment variables to `configuration.yaml` /
  `secrets.yaml`** inside the config directory. Only `LEARNINGHOUSE_CONFIG_DIRECTORY` (where those
  two files live) is still read from the environment. Run `learninghouse-migrate-config` once
  against your existing config directory (console) or mounted volume (Docker) before upgrading -
  see the README's "Upgrading from `LEARNINGHOUSE_*` environment variables" section. The script
  only migrates settings, never brain data, sensors, or the security database.
- `jwt_secret` now persists in `secrets.yaml`, generated once on first start instead of being
  regenerated on every process start - existing sessions no longer get invalidated by a restart.
