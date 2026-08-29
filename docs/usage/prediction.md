# Prediction

To predict a new data set with your brain, send a `POST` request.

!!! note "Authorization"
    You need an administration JWT or an API key with the role `trainer` or `user` for this
    request. See [Security](../configuration/security.md).

```bash
# URL is http://host:5000/api/brain/:name/prediction
curl --location --request POST 'http://localhost:5000/api/brain/darkness/prediction' \
    --header 'Content-Type: application/json' \
    --header 'X-LEARNINGHOUSE-API-KEY: YOURSECRETKEY' \
    --data-raw '{
        "azimuth": 321.4441223144531,
        "elevation": -19.691608428955078,
        "rain_gauge": 0.0,
        "pressure_trend_1h": "falling"
    }'
```

You only have to send the sensors the brain actually uses as `features`.

## Missing values

If one of your sensors used as a `feature` in the brain is not working at the moment and is not
sending a value, the service handles this using the following rules. For `categorical data` all
categorical columns are set to zero. For `numerical data` the mean of all known training set
values (see [Test size](../configuration/brains.md#test-size)) for this `feature` is assumed.
