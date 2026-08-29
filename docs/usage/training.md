# Train the brain

## Send a data point and train

To train, send a `PUT` request to the service.

!!! note "Authorization"
    You need an administration JWT or an API key with the role `trainer` for this request. See
    [Security](../configuration/security.md).

```bash
# URL is http://<host>:5000/api/brain/:name/training
curl --location --request PUT 'http://localhost:5000/api/brain/darkness/training' \
    --header 'Content-Type: application/json' \
    --header 'X-LEARNINGHOUSE-API-KEY: YOURSECRETKEY' \
    --data-raw '{
        "dependent_value": true,
        "sensors_data": {
            "azimuth": 321.4441223144531,
            "elevation": -19.691608428955078,
            "rain_gauge": 0.0,
            "pressure": 971.0,
            "pressure_trend_1h": "falling",
            "temperature_outside": 23.0,
            "temperature_trend_1h": "rising",
            "light_state": false
        }
    }'
```

You can send a field `timestamp` with your dataset containing a UNIX timestamp, or the service
adds this information with its current time. The service generates some further time-relevant
fields inside the training dataset that you can also use as `features`. These are
`month_of_year`, `day_of_month`, `day_of_week`, `hour_of_day` and `minute_of_hour`.

If one of your sensors is not working at the moment and therefore not sending a value, the service
adds a value using the following rules. For `categorical data` all categorical columns are set to
zero. For `numerical data` the mean of all known training set values (see
[Test size](../configuration/brains.md#test-size)) for this `feature` is assumed.

## Retrain with existing data

To train the brain with the data it already has, for example after a service update, use a `POST`
request without a body.

!!! note "Authorization"
    You need an administration JWT or an API key with the role `trainer` for this request. See
    [Security](../configuration/security.md).

```bash
# URL is http://host:5000/api/brain/:name/training
curl --location \
    --header 'X-LEARNINGHOUSE-API-KEY: YOURSECRETKEY' \
    --request POST 'http://localhost:5000/api/brain/darkness/training'
```

## Information about a trained brain

To obtain information about a trained brain, use a `GET` request.

!!! note "Authorization"
    You need an administration JWT or an API key with the role `trainer` or `user` for this
    request. See [Security](../configuration/security.md).

```bash
# URL is http://host:5000/api/brain/:name/info
curl --location \
    --header 'X-LEARNINGHOUSE-API-KEY: YOURSECRETKEY' \
    --request GET 'http://localhost:5000/api/brain/darkness/info'
```

The response carries the score, the feature list, and the library versions the model was trained
with. A brain trained under a different scikit-learn or service version is rejected rather than
loaded best-effort - retrain it with the `POST` request above.
