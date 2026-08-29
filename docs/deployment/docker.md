# Docker

```bash
docker pull ghcr.io/learninghouseservice/learninghouse:latest
```

Images are published to
[ghcr.io](https://github.com/LearningHouseService/learninghouse/pkgs/container/learninghouse) and
to [Docker Hub](https://hub.docker.com/r/learninghouseservice/learninghouse), for `linux/amd64`
and `linux/arm64`.

## Run it

```bash
docker run --name learninghouse --rm \
    -v brains:/learninghouse/brains \
    -p 5000:5000 \
    -e "TZ=Europe/Berlin" \
    ghcr.io/learninghouseservice/learninghouse:latest
```

The service is then at <http://localhost:5000/>, the [UI](../usage/ui.md) at
<http://localhost:5000/ui>.

## The volume

`/learninghouse/brains` is the configuration directory inside the image, declared as a `VOLUME`.
Everything the service persists lives there - `configuration.yaml`, `secrets.yaml`, your sensor
declarations, the security database, and one subdirectory per brain with its training data and
trained model. See [Installation](../getting-started/installation.md#prepare-the-configuration-directory)
for the full layout.

**Back up this volume.** A lost volume means retraining every brain from scratch, and losing the
API keys and the administration password with it.

The container runs as an unprivileged user with UID 1000. A bind mount has to be writable by that
UID:

```bash
mkdir -p ./brains && sudo chown 1000:1000 ./brains
docker run --name learninghouse --rm \
    -v ./brains:/learninghouse/brains \
    -p 5000:5000 \
    ghcr.io/learninghouseservice/learninghouse:latest
```

## Configuration

The image ships a default `configuration.yaml` at `/learninghouse/brains/configuration.yaml`:

```yaml
host: 0.0.0.0
port: 5000
```

`host: 0.0.0.0` is what makes the service reachable from outside the container - the service's own
default of `127.0.0.1` would only ever answer requests originating inside it.

There are three ways to change it:

1. **Pre-populate the volume** with your own `configuration.yaml` before the container's first
   start. Docker seeds a fresh named volume from the image directory it is mounted over, so an
   existing volume's own file wins over the baked-in one.
2. **Mount a file over that path**:
   `-v $(pwd)/configuration.yaml:/learninghouse/brains/configuration.yaml:ro`.
3. **Edit the file in the volume** and restart the container.

Keep `host: 0.0.0.0` in whatever you replace it with, and publish the port with `-p` rather than
binding the service to a narrower address inside the container.

!!! warning "`LEARNINGHOUSE_*` environment variables are gone"
    Older images read `LEARNINGHOUSE_HOST`, `LEARNINGHOUSE_PORT` and everything else from the
    environment. They are no longer read. Only `LEARNINGHOUSE_CONFIG_DIRECTORY` remains, and the
    image already points it at the volume. See
    [Migration](../migration/environment-variables.md).

## Timezone

`-e TZ=Europe/Berlin` matters more than it looks: training rows get `month_of_year`,
`day_of_month`, `day_of_week`, `hour_of_day` and `minute_of_hour` derived from the service's local
time, and those are usable as features. A container running on UTC while your house runs on local
time learns the wrong daily rhythm.

## Next steps

- [Docker Compose](docker-compose.md)
- [Configuration reference](../configuration/index.md)
