# Configuration reference

The service is configured by two files inside the configuration directory (`brains` by default):

- **`configuration.yaml`** - everything except secrets.
- **`secrets.yaml`** - sensitive values, never read from `configuration.yaml`, the environment, or
  written to logs.

Neither file needs to exist. Every setting has a default, and `secrets.yaml`'s `jwt_secret` is
generated and written on first start if it isn't already there.

Where the two files live is itself set by one environment variable, because it has to be resolved
before either file can be read:

| Environment variable | Default | Description |
|---|---|---|
| `LEARNINGHOUSE_CONFIG_DIRECTORY` | `./brains` | The directory holding `configuration.yaml` and `secrets.yaml`, and everything else the service persists. |

`config_directory` is deliberately *not* settable from inside `configuration.yaml` - it is the
value that determined where that file was read from.

## `configuration.yaml`

| Key | Default (production/development) | Description |
|---|---|---|
| `environment` | `production` | Choose the default environment settings: `production` or `development`. |
| `title` | `learningHouse Service` | Set the name of the service. |
| `host` | `127.0.0.1` | The address the service binds to. Use `0.0.0.0` for all available interfaces. |
| `port` | `5000` | The port the service listens on. |
| `workers` | `1` | Count of parallel workers for processing. Only `1` works today, see the warning below. |
| `base_url` | *not set* | Base URL for external access, for example the hostname of your Docker host. |
| `openapi_file` | `/learninghouse_api.json` | File URL path to the OpenAPI JSON file. |
| `docs_url` | `/docs` | URL path for the interactive [API documentation](../usage/api.md). Leave it empty to disable the documentation. |
| `jwt_expire_minutes` | `10` | The refresh token of JWTs expires after this many minutes. |
| `cors_allowed_origins` | *empty* | Additional origins allowed to send credentialed cross-origin requests, as a YAML list. The service's own origin is always allowed. See [CORS](security.md#cors). |
| `allow_api_key_query` | `False` | Accept API keys from the `?api_key=` query parameter. Deprecated, see [API keys](security.md#api-keys). |
| `logging_level` | `INFO` | One of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. |
| `debug` | `False` / `True` | The debugger is activated automatically in the development environment. For security reasons it is recommended not to activate it in production. |
| `reload` | `False` / `True` | The source is reloaded automatically in the development environment. For security reasons it is recommended not to activate it in production. |

Setting `environment: development` changes the defaults of `debug`, `reload`, `title` and
`cors_allowed_origins` (which gains `http://localhost:4200` for `ng serve`) - an explicit value for
any of those still wins.

!!! warning "`workers` above 1 does not work yet"
    Refresh tokens and the security database are held per process, so a session issued by one
    worker is rejected by every other one, and a password change or a new API key made through one
    is invisible to the rest. Keep `workers` at `1` until both live in shared storage.

## `secrets.yaml`

| Key | Default | Description |
|---|---|---|
| `jwt_secret` | *generated on first start and persisted* | After an administration login a JWT is generated and signed with this secret. Because it is persisted, sessions survive a restart. |

The file is written with mode `0600`. Set the value yourself only if you need to pin it - for
example to share it across several processes.

## Everything else

Sensors, brains, the administration password and the API keys are not part of these files. They
are configured through the [UI](../usage/ui.md) or the API and stored in the same directory:

- [Sensors](sensors.md)
- [Brains](brains.md)
- [Security](security.md)
