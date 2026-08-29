# Sensors

Send data from all sensors to the **learningHouse Service**, especially when training your brains.
The service saves all data fields, even if they are not currently used as a `feature`. It chooses
the best feature set each time you train a brain.

## Numerical and categorical data

Sensor data divides into two types. `Numerical data` can be processed directly by your models,
while `Categorical data` has to be preprocessed by the service before it can be used as a
`feature`. Categorical data can be identified with a simple rule:

- Non-numerical values, **or**
- Numerical values that can be described using terms.

Examples of categorical data:

- `pressure_trend`: values of `falling`, `rising`, `consistent`
- `month_of_year`: 1 *(January)*, 2 *(February)*, …
- `weather_condition`: `sunny`, `cloudy`
- `switch`: `ON`, `OFF`

## Declaring your sensors

To let the service use your sensor data as `features`, tell it the data type of each sensor. Add
each sensor you want to use via the [UI](../usage/ui.md).

For example, add the following sensors:

| Name | Type |
|---|---|
| `azimuth` | numerical |
| `elevation` | numerical |
| `rain_gauge` | numerical |
| `pressure` | numerical |
| `pressure_trend_1h` | categorical |
| `temperature_outside` | numerical |
| `temperature_trend_1h` | categorical |
| `light_state` | categorical |

The declarations are stored as `sensors.json` in the configuration directory.

## Time fields you get for free

Every training data point also gets `month_of_year`, `day_of_month`, `day_of_week`, `hour_of_day`
and `minute_of_hour`, derived from the row's timestamp. You can use them as features without
declaring or sending them. See [Training](../usage/training.md).

## Missing values

If one of your sensors is not working at the moment and therefore not sending a value, the service
fills it in:

- **Categorical data**: all categorical columns for that sensor are set to zero.
- **Numerical data**: the mean of all known training set values for that feature is assumed.

## Changing the configuration over the API

Sensors can also be configured through the API rather than the UI. See the
[API documentation](../usage/api.md) served by the running service.
