# Docker Compose

```yaml
services:
  learninghouse:
    image: ghcr.io/learninghouseservice/learninghouse:latest
    container_name: learninghouse
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      TZ: Europe/Berlin
    volumes:
      - brains:/learninghouse/brains

volumes:
  brains:
```

```bash
docker compose up -d
```

The service is then at <http://localhost:5000/>, the [UI](../usage/ui.md) at
<http://localhost:5000/ui>.

## With your own configuration file

To keep `configuration.yaml` next to the compose file instead of inside the volume, mount it over
the path the image ships its default at:

```yaml
services:
  learninghouse:
    image: ghcr.io/learninghouseservice/learninghouse:latest
    container_name: learninghouse
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      TZ: Europe/Berlin
    volumes:
      - brains:/learninghouse/brains
      - ./configuration.yaml:/learninghouse/brains/configuration.yaml:ro

volumes:
  brains:
```

Keep `host: 0.0.0.0` in that file - see [Docker](docker.md#configuration) for why. `secrets.yaml`
and everything else still lives in the `brains` volume, which is the thing to back up.

## Updating

```bash
docker compose pull
docker compose up -d
```

A service update can invalidate trained models: a brain records the library versions it was
trained with and is rejected rather than loaded best-effort when they no longer match. Retrain it
with the `POST` request in [Training](../usage/training.md#retrain-with-existing-data) - the
training data in the volume is kept, so no data has to be resent.
