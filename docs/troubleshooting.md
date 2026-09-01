# Troubleshooting

## Every endpoint returns an error except login

The administration account is still on the [fallback password](configuration/security.md#fallback-password)
`learninghouse`. Until it is changed, all other endpoints stay deactivated by design. Change it on
the initial login screen of the [UI](usage/ui.md).

## After an upgrade my password is `learninghouse` again and the API keys are gone

Credentials hashed by a release before argon2id are not carried over - those hashes cannot be read
any more, and API keys are not recoverable from their stored form in any case. Log in with
`learninghouse`, set a new password, create the keys again and update the clients that use them.
See [Security](configuration/security.md#fallback-password).

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
and the security database are held per process, so a session issued by one worker is rejected by
every other one. Keep `workers` at `1` until both live in shared storage.

## A request from my own dashboard is blocked by the browser

The browser console says the response has no `Access-Control-Allow-Origin` header, or a preflight
returned `400`. Only the service's own origin may send credentialed cross-origin requests unless
you say otherwise. Add the page's origin - scheme, host and port, no path, no trailing slash - to
`cors_allowed_origins` in `configuration.yaml` and restart:

```yaml
cors_allowed_origins:
  - http://homeassistant.local:8123
```

`*` is refused: with credentials it would let every page you visit call your instance with your
session. See [CORS](configuration/security.md#cors).

## A request with `?api_key=` returns 403 `APIKEY_IN_QUERY`

The query parameter is deprecated - query strings are written to access logs, proxy logs and
browser history. Send the key as the header `X-LEARNINGHOUSE-API-KEY` instead. If a client cannot
be changed straight away, set `allow_api_key_query: true` in `configuration.yaml` while you
migrate it, and replace that key afterwards. See
[API keys](configuration/security.md#api-keys).

## The learned daily rhythm is off by hours

Training rows derive `hour_of_day` and friends from the service's local time. In a container
without `TZ` set that is UTC. Pass `-e TZ=Europe/Berlin` (or your own zone) and retrain. See
[Docker](deployment/docker.md#timezone).

## An API key stopped working, or I lost it

An API key is displayed once and cannot be requested again. Delete it in the [UI](usage/ui.md) and
create a new one - and note that keys from a release before argon2id are not carried over, see
above. Check that you send it as the header `X-LEARNINGHOUSE-API-KEY` rather than as `?api_key=`,
which is no longer accepted, and that its role covers the endpoint - `user` is prediction only, `trainer` is training and prediction. See
[Security](configuration/security.md#api-keys).

## Getting more detail

Set `logging_level: DEBUG` in `configuration.yaml` and restart. If it still makes no sense, ask on
[Discord](https://discord.gg/U9axHEYqqB) or open an
[issue](https://github.com/LearningHouseService/learninghouse/issues).
