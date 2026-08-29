# Installation

## With pip

```bash
pip install -U learninghouse
```

## With Docker

```bash
docker pull ghcr.io/learninghouseservice/learninghouse:latest
```

Images are published for `linux/amd64` and `linux/arm64`.

## Prepare the configuration directory

```bash
mkdir -p brains
```

The `brains` directory is where the service keeps everything it persists. By default it is
`./brains`, relative to the working directory the service was started in; see
[`LEARNINGHOUSE_CONFIG_DIRECTORY`](configuration.md#the-one-environment-variable) for how to put
it somewhere else.

It holds:

| Path | Contents |
|---|---|
| `configuration.yaml` | Service settings. Optional - every setting has a default. |
| `secrets.yaml` | Sensitive values, currently only `jwt_secret`. Written on first start if missing. |
| `sensors.json` | Your sensor declarations. |
| `security.json` | The administration password hash and the API keys. |
| `<brain>/config.json` | That brain's configuration. |
| `<brain>/training_data.csv` | Every data point ever sent for that brain. |
| `<brain>/trained.pkl` | The trained model, dumped to disk. |
| `<brain>/info.json` | Score, feature list and the library versions the model was trained with. |

There is one subdirectory per brain, holding all files relevant to that brain. The models are the
brains of your learning house.

## Next steps

- [First configuration](configuration.md)
- [Run the service](running.md)
