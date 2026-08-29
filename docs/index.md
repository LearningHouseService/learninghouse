# learningHouse Service

The **learningHouse Service** provides machine learning algorithms based on the
[scikit-learn](https://scikit-learn.org/) Python library as a RESTful API. Its purpose is to offer
smart home enthusiasts an easy way to teach their homes.

You push sensor data into the service, tell it what the right answer was, and it learns the
connection. A *brain* is one such trained model: "is it dark enough to switch the light on?",
"which setpoint should the heating run at?" - whatever your own house does, learned from your own
house's data.

## What it does

- **Brains**: named models, each one a `classifier` for categorical answers or a `regressor` for
  numerical ones, built on scikit-learn's random forest estimators.
- **Sensors**: your data fields, declared once as `numerical` or `categorical`, preprocessed for
  you.
- **Training and prediction over REST**, so any home automation system that can send an HTTP
  request can use it.
- **Automatic time features**: month, day, weekday, hour and minute are derived from every
  training row, ready to be used as features.
- **Missing sensor values are handled**, not rejected - categorical columns go to zero, numerical
  ones to the training set's mean.
- **A small web UI** for configuring sensors, brains, API keys and the administration password.
- **Docker images** for `linux/amd64` and `linux/arm64`.

## Where to start

<div class="grid cards" markdown>

- **New here?**

    Install the service and prepare its configuration directory.

    [Installation](getting-started/installation.md)

- **Setting it up?**

    Every `configuration.yaml` key, plus sensors, brains and security.

    [Configuration reference](configuration/index.md)

- **Teaching a brain?**

    Send training data, train, and predict.

    [Training](usage/training.md)

- **Upgrading to 2.0.0?**

    `LEARNINGHOUSE_*` environment variables are no longer read.

    [Migration](migration/environment-variables.md)

</div>

## Getting help

- Ask on [Discord](https://discord.gg/U9axHEYqqB).
- Share ideas, suggestions and problems as an
  [issue](https://github.com/LearningHouseService/learninghouse/issues). We are really looking
  forward to your feedback.
