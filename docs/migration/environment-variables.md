# Upgrading to 2.0.0 from `LEARNINGHOUSE_*` environment variables

Up to and including 1.11.0, every setting was read from `LEARNINGHOUSE_*` environment variables
and from an optional `.env` file. **2.0.0 replaces that with `configuration.yaml` and
`secrets.yaml`**, which is what the major version number is for.

**This is a breaking change.** Environment variables other than `LEARNINGHOUSE_CONFIG_DIRECTORY`
are no longer read. Nothing falls back to them, and a 2.0.0 service started with the old variables
set will simply run on its defaults - no error, no warning, just a service that is not configured
the way you configured it.

A one-shot migration script converts the old layout for you. It only touches settings - never
brain data, sensors, or the security database. Why it is a script run once rather than a permanent
fallback is recorded in
[decision 0002](../decisions/0002-yaml-configuration-with-a-one-shot-migration.md).

Run the migration **while 1.11.0 is still installed, or from the 2.0.0 image without starting the
service** - the script reads the environment it is given, so the variables have to still be set in
the shell or the `--env-file` you run it with.

## Console

Run once from wherever your old `.env` / environment lived, before starting 2.0.0:

```bash
learninghouse-migrate-config --config-directory ./brains
```

## Docker

Run once against the mounted volume before switching the container over to 2.0.0, reusing the same
`.env` / `LEARNINGHOUSE_*` variables the old container was started with. The `2.0.0` image is what
ships the script, so pull that tag and run the script from it rather than the service:

```bash
docker run --rm --env-file .env \
    -v brains:/learninghouse/brains \
    ghcr.io/learninghouseservice/learninghouse:2.0.0 \
    learninghouse-migrate-config --config-directory /learninghouse/brains
```

## What it does

- Reads every `LEARNINGHOUSE_*` variable set in the process environment, and `.env` if present.
- Writes the non-sensitive ones into `configuration.yaml` at the target configuration directory.
- Writes the sensitive ones - currently `jwt_secret` - into `secrets.yaml`, using the same field
  list the settings loader itself uses, so the two cannot drift apart.
- Refuses to overwrite an existing `configuration.yaml` / `secrets.yaml` unless you pass
  `--force`, so re-running it after a manual edit won't silently clobber it.

## What it does not do

- It does not touch brain configurations, training data or trained models.
- It does not touch `sensors.json` or the security database.
- It does not run on every start. Run it once, on upgrade, by hand.

## After migrating

Check the result against the [configuration reference](../configuration/index.md), then start
2.0.0 normally. `LEARNINGHOUSE_CONFIG_DIRECTORY` is the one variable you keep setting if your
configuration directory is not `./brains`.

Drop the old `LEARNINGHOUSE_*` variables from your `.env`, your systemd unit or your compose file
once the service comes up correctly. Leaving them set does nothing, but the next person to read
that file will believe they are still in effect.

!!! note "Retrain your brains after upgrading"
    2.0.0 also carries a scikit-learn update. A brain records the library versions it was trained
    with and is rejected rather than loaded best-effort when they no longer match. The training
    data is untouched by this migration, so a retrain needs no data resent - see
    [Training](../usage/training.md#retrain-with-existing-data).
