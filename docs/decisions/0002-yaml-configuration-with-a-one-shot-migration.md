# 2. YAML configuration, with a one-shot migration instead of an env-var fallback

- **Status:** accepted
- **Date:** 2026-08-29

## Context

`ServiceSettings.__init__` merged three sources in order: `_read_environment` (`LEARNINGHOUSE_*`
variables), `_read_dotenv` (an optional `.env` file), and `_read_secrets` (Docker secrets under
`/run/secrets`). All three are ways of avoiding one readable configuration file, and each of them
had to be understood to answer "where does this value come from?".

Two things made that arrangement worse rather than merely inelegant:

- `jwt_secret` defaulted to a fresh `token_hex(16)` per process start. Every restart invalidated
  every session, and with `workers > 1` each worker signed with its own secret, so a token issued
  by one was rejected by another.
- The Home Assistant add-on planned for a later phase reads its configuration from a mapped `/data`
  directory. A file is what it wants; a set of environment variables is not.

`solaredge2mqtt`, the sibling project, already runs a `configuration.yaml` / `secrets.yaml` split.

## Decision

`ServiceSettings` reads `configuration.yaml` for everything that used to be a `LEARNINGHOUSE_*`
variable, and `secrets.yaml` for values that must never be readable from the general configuration
file or from logs.

- **One bootstrap value stays an environment variable.** `LEARNINGHOUSE_CONFIG_DIRECTORY` has to be
  resolvable before either YAML file can be located. It is therefore also the one key that
  `configuration.yaml` cannot set: it is the value that determined where that file was read from.
- **The split is driven by one shared field list.** `SECRET_FIELDS` in the settings module is
  excluded from the `configuration.yaml` merge and is what the migration script routes to
  `secrets.yaml`, so the loader and the script cannot drift apart on what counts as sensitive.
- **`jwt_secret` gets its persistent home here, not in the later persistence phase.** It is
  generated once on first read and written to `secrets.yaml` with mode `0600`. Putting it in the
  planned SQLite database instead would have meant waiting a phase, and turning one value into a
  table with one row.
- **The Docker image bakes in a default `configuration.yaml`** (`host: 0.0.0.0`, `port: 5000`)
  instead of the `LEARNINGHOUSE_HOST` / `LEARNINGHOUSE_PORT` image `ENV` values it used to carry.
  Docker seeds a fresh named volume from the image directory mounted over it, so a first start
  still picks this up while an existing volume's own file wins.
- **Migration is a one-shot script, not a runtime fallback.** `learninghouse-migrate-config` reads
  every `LEARNINGHOUSE_*` variable in the process environment, and `.env` if present, and writes
  the `configuration.yaml` / `secrets.yaml` pair. It refuses to overwrite existing files without
  `--force`. It runs on upgrade, by hand, once.

## Consequence

**This is a breaking change**, recorded as such in the changelog. An installation upgraded without
running the script starts on defaults, silently, because nothing reads the old variables any more.
That is the cost accepted for not keeping two settings paths alive indefinitely: a deprecated
fallback would have had to survive every later phase that touches configuration, and would have
made "where does this value come from?" a three-source question forever.

The rejected alternative was the usual one - read the environment when the YAML key is absent, log
a deprecation warning, remove it in some later major version. It was rejected because the removal
never happens on schedule, and because the add-on phase would have shipped with both paths still
live.

Sessions surviving a restart, which the security phase lists as an acceptance criterion, is
satisfied by this decision rather than by that phase. What remains there is the multi-worker half:
refresh tokens are still a per-process dictionary, so `workers` must stay at `1`.

The migration script is deliberately narrow. It touches settings only - never brain
configurations, training data, trained models, `sensors.json`, or the security database. Anything
it does not understand is not silently dropped into a file the service then reads as
configuration.
