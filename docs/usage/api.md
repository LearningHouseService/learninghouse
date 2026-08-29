# API documentation

The service serves its own interactive API documentation. With the service running, open
<http://localhost:5000/docs>.

This site deliberately does not restate the endpoint list. The service's OpenAPI document is
generated from the code that actually handles the requests, so it cannot go stale the way a second
hand-written copy would.

Two settings in [`configuration.yaml`](../configuration/index.md#configurationyaml) control it:

| Key | Default | Effect |
|---|---|---|
| `docs_url` | `/docs` | Where the interactive documentation is served. Leave it empty to disable it. |
| `openapi_file` | `/learninghouse_api.json` | Where the raw OpenAPI JSON document is served. |

If you set `base_url`, both URLs are reported relative to it - useful when the service sits behind
a reverse proxy or in a container with a different external hostname.

What the endpoints are used for is documented here:

- [Training](training.md)
- [Prediction](prediction.md)
- [Sensors](../configuration/sensors.md) and [brains](../configuration/brains.md) can be
  configured over the API too, not only through the UI.
- [Authorization](../configuration/security.md) applies to all of them.
