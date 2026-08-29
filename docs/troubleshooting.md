# Troubleshooting

## Every endpoint returns an error except login

The administration account is still on the [fallback password](configuration/security.md#fallback-password)
`learninghouse`. Until it is changed, all other endpoints stay deactivated by design. Change it on
the initial login screen of the [UI](usage/ui.md).

## My settings are ignored after an upgrade

`LEARNINGHOUSE_*` environment variables are no longer read - only
`LEARNINGHOUSE_CONFIG_DIRECTORY`. Everything else has to be in `configuration.yaml`. Run the
migration script once: [Migration](migration/environment-variables.md).

## The service is not reachable from another machine

`host` defaults to `127.0.0.1`, which only answers requests from the local machine. Set
`host: 0.0.0.0` in `configuration.yaml`. In Docker the image already does this - check that you
published the port with `-p 5000:5000` and that a `configuration.yaml` you mounted yourself did
not overwrite the `host` setting.

## A brain is rejected after an update

A brain records the service and library versions it was trained with. When those no longer match,
it is rejected rather than loaded best-effort - a model built by a different scikit-learn release
can silently mispredict, which is worse than an error.

Retrain it with the existing data; nothing has to be resent:

```bash
curl --location \
    --header 'X-LEARNINGHOUSE-API-KEY: YOURSECRETKEY' \
    --request POST 'http://localhost:5000/api/brain/darkness/training'
```

## Training does not start

Training of a brain starts when there are at least 10 data points. Keep sending training data
until it does. See [Training](usage/training.md).

## The accuracy score is poor

A score between 80% and 90% is considered good. Below 80% the brain is underfitted, above 90% it
is overfitted, and both predict new data points badly. Adjust the
[estimator configuration](configuration/brains.md#estimator) - `estimators` and `max depth` - or
add more training data.

## Sessions are lost on restart, or logins fail at random

`jwt_secret` lives in `secrets.yaml` and is generated on first start, so sessions do survive a
restart. If they do not, the configuration directory is not persistent - in Docker, check that
`/learninghouse/brains` is on a volume.

Random logouts with a persistent secret point at `workers` being greater than `1`. Refresh tokens
are held per process, so a token issued by one worker is rejected by another. Keep `workers` at
`1`.

## The learned daily rhythm is off by hours

Training rows derive `hour_of_day` and friends from the service's local time. In a container
without `TZ` set that is UTC. Pass `-e TZ=Europe/Berlin` (or your own zone) and retrain. See
[Docker](deployment/docker.md#timezone).

## An API key stopped working, or I lost it

An API key is displayed once and cannot be requested again. Delete it in the [UI](usage/ui.md) and
create a new one. Check that you send it as the header `X-LEARNINGHOUSE-API-KEY`, and that its
role covers the endpoint - `user` is prediction only, `trainer` is training and prediction. See
[Security](configuration/security.md#api-keys).

## Getting more detail

Set `logging_level: DEBUG` in `configuration.yaml` and restart. If it still makes no sense, ask on
[Discord](https://discord.gg/U9axHEYqqB) or open an
[issue](https://github.com/LearningHouseService/learninghouse/issues).
