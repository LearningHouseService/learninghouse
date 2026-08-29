# Brains

A brain is one trained model with a name. It has a set of `features` taken from your
[sensors](sensors.md), a `dependent` variable it predicts, and an estimator configuration.

## Example brain

The brain decides whether it is dark enough to switch the light on. It uses a machine learning
algorithm called `RandomForestClassifier`.

To add a new brain via the [UI](../usage/ui.md), log in with your administration account and
provide the following parameters:

| Field | Value |
|---|---|
| Name | `darkness` |
| Typed | Classifier |
| Dependent encode | True |
| Test size | 0.2 |
| Estimators | 100 |
| Max depth | 5 |

The brain's configuration is stored as `config.json` inside the brain's own subdirectory of the
configuration directory.

## Configuration parameters

### Estimator

The learningHouse Service can predict values using an estimator. An estimator can be of type
`classifier`, which is best suited for categorical outputs such as true and false. If you want to
predict a numerical value, such as the setpoint of a heating system, use the type `regressor`
instead.

For both types the service uses a machine learning algorithm called random forest estimation. This
algorithm builds a "forest" of decision trees from your `features` and takes the mean of the
predictions of all of them to give you the best result. For more details see the API description
of scikit-learn:

| Estimator type | API reference |
|---|---|
| `RandomForestRegressor` | <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html> |
| `RandomForestClassifier` | <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html> |

You can adjust the number of decision trees with the `estimators` option (default: 100), and the
maximum depth of each tree with the `max depth` option (default: 5). Both are optional. Try
resizing these values to optimize the accuracy of your model.

### Dependent variable

The `dependent` variable is the one that must be included in the training data and is predicted by
the trained brain. It is the same as the `name` variable.

The `dependent` variable must be a number. If it is not a number but a string or a boolean
(true/false), as in the example above, set `dependent encode` to yes.

### Test size

The service only uses a portion of your training data to train the brain. The remaining portion,
specified by `test size`, is used to score the accuracy of your brain.

You can specify the `test size` as a percentage, using floating point numbers between 0.01 and
0.99, or as an absolute number of data points, using integers.

A `test size` of 20% (`0.2`) should be sufficient to start with.

An accuracy score between 80% and 90% is considered good. Scores below 80% indicate that the brain
is underfitted; scores above 90% indicate that it is overfitted. Both cases can result in poor
predictions for new data points. Try adjusting the [estimator configuration](#estimator) to
improve the score.

Training of the brain starts when there are at least 10 data points.

## Changing the configuration over the API

Brains can also be configured through the API rather than the UI. See the
[API documentation](../usage/api.md) served by the running service.
