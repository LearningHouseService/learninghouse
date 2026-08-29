# First configuration

The service is configured by two files inside the configuration directory (`brains` by default):
`configuration.yaml` for everything except secrets, and `secrets.yaml` for sensitive values.

**Neither file needs to exist.** Every setting has a default, and `secrets.yaml`'s `jwt_secret` is
generated and written on first start if it isn't already there. You only write a
`configuration.yaml` to change something.

## The one environment variable

Exactly one thing is still set via an environment variable, because it has to be known before
either YAML file can be located:

| Environment variable | Default | Description |
|---|---|---|
| `LEARNINGHOUSE_CONFIG_DIRECTORY` | `./brains` | The directory holding `configuration.yaml`, `secrets.yaml`, and everything else the service persists. |

Every other setting lives in `configuration.yaml`. If you are coming from a version that read
`LEARNINGHOUSE_*` variables for everything, read
[Migration](../migration/environment-variables.md) first - those variables are no longer read.

## Start from the examples

Copy
[configuration.yaml.example](https://raw.githubusercontent.com/LearningHouseService/learninghouse/main/core/configuration.yaml.example)
to `configuration.yaml` and
[secrets.yaml.example](https://raw.githubusercontent.com/LearningHouseService/learninghouse/main/core/secrets.yaml.example)
to `secrets.yaml`, both inside your configuration directory, and uncomment or change what you
need. Every value in the example file is commented out and shows the default.

A minimal `configuration.yaml` that makes the service reachable from other machines:

```yaml
host: 0.0.0.0
port: 5000
```

!!! warning "Only bind to `0.0.0.0` behind something you trust"
    The default `127.0.0.1` means the service is reachable from the local machine only. Before
    exposing it, read [Security](../configuration/security.md) - the administration account starts
    on a well-known fallback password.

## Next steps

- [Run the service](running.md)
- [The full configuration reference](../configuration/index.md)
