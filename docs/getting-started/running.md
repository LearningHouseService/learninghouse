# Run the service

## In the console

Copy
[configuration.yaml.example](https://raw.githubusercontent.com/LearningHouseService/learninghouse/main/core/configuration.yaml.example)
to `configuration.yaml` inside your configuration directory and modify it according to your needs.

Then simply run:

```bash
learninghouse
```

By default the service listens on <http://localhost:5000/>.

To use a configuration directory somewhere other than `./brains`:

```bash
LEARNINGHOUSE_CONFIG_DIRECTORY=/etc/learninghouse learninghouse
```

## With Docker

```bash
docker run --name learninghouse --rm \
    -v brains:/learninghouse/brains \
    -p 5000:5000 \
    -e "TZ=Europe/Berlin" \
    ghcr.io/learninghouseservice/learninghouse:latest
```

See [Deployment](../deployment/docker.md) for the details, including how to override the
configuration the image ships with.

## What to do next

1. Open the [UI](../usage/ui.md) at <http://localhost:5000/ui> and change the administration
   password - until you do, every other endpoint stays disabled. See
   [Security](../configuration/security.md).
2. Declare your [sensors](../configuration/sensors.md).
3. Create a [brain](../configuration/brains.md).
4. [Train it](../usage/training.md) and [predict](../usage/prediction.md) with it.
