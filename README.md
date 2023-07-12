# learningHouse Service 
[![License](https://img.shields.io/github/license/LearningHouseService/learninghouse)](https://github.com/LearningHouseService/learninghouse/blob/main/LICENSE) [![Release](https://img.shields.io/github/v/release/LearningHouseService/learninghouse)](https://github.com/LearningHouseService/learninghouse/releases/latest) [![Build Status](https://img.shields.io/github/actions/workflow/status/LearningHouseService/learninghouse/build_project.yml?branch=main)](https://github.com/LearningHouseService/learninghouse/actions/workflows/build_project.yml) [![PyPI version](https://img.shields.io/pypi/v/learninghouse.svg)](https://pypi.org/project/learninghouse/) [![Discord Chat](https://img.shields.io/discord/997393653758697482)](https://discord.gg/U9axHEYqqB)

![learningHouse Logo](https://raw.githubusercontent.com/LearningHouseService/learninghouse/main/artwork/learninghouse_logo.svg)

## Introduction

The **LearningHouse Service** provides machine learning algorithms based on the scikit-learn python library as a RESTful API. Its purpose is to offer smart home enthusiasts an easy way to teach their homes.

## Contact and Feedback

If you have any questions, please contact us on Discord.

[![Discord Banner](https://discordapp.com/api/guilds/997393653758697482/widget.png?style=banner2)](https://discord.gg/U9axHEYqqB)

Please share your ideas on what you want to teach your home, suggestions or problems by opening an [issue](https://github.com/LearningHouseService/learninghouse/issues). We are really looking forward to your feedback.

## Installation and Configuration

Install and update using pip.
```
pip install -U learninghouse
```

Install and update using docker
```
docker pull ghcr.io/learninghouseservice/learninghouse:latest
```

### Prepare configuration directory
```
mkdir -p brains
```

The `brains` directory holds the model configuration as a json file. The models are the brains of your learning house.

There will be one subdirectory per brain, where all files relevant for a brain will be stored.
The brain subdirectory needs a `config.json` file holding the basic configuration. The service will store a `training_data.csv` file holding
all data from your sensors and an object dump of the trained model to a file called `trained.pkl`.

### Service configuration

The service is configured by environment variables. The following options can be set:

Environment Variable             | default (production/development) | description                                            
-------------------------------- | -------------------------------- | ------------------------------------------------------ 
LEARNINGHOUSE_ENVIRONMENT        | production                       | Choose the default environment settings: production or development. 
LEARNINGHOUSE_HOST               | 127.0.0.1                        | Set the address that the service should bind to. (use 0.0.0.0 for all available)
LEARNINGHOUSE_PORT               | 5000                             | Set the port on which the service should listen.
LEARNINGHOUSE_BASE_URL           | _Not set_                        | Set the base URL for external access, for example, the hostname of your Docker host.
LEARNINGHOUSE_CONFIG_DIRECTORY   | ./brains                         | Define the directory where all configuration data goes.
LEARNINGHOUSE_OPENAPI_FILE       | /learninghouse_api.json          | Provide the file URL path to the OpenAPI JSON file.
LEARNINGHOUSE_DOCS_URL           | /docs                            | Define the URL path for the interactive [API documentation](#api-documentation). If you leave it empty, the documentation will be disabled.
LEARNINGHOUSE_JWT_SECRET         | _Generated on startup_           | For administration authentication, a JWT is generated after login. This JWT is signed with a secret. By default, it is generated on startup, which will invalidate existing JWTs on each restart.
LEARNINGHOUSE_JWT_EXPIRE_MINUTES | 10                               | The refresh token of JWTs will expire after a given amount of minutes.
LEARNINGHOUSE_LOGGING_LEVEL      | INFO                             | Set logging level to DEBUG, INFO, WARNING, ERROR, CRITICAL
LEARNINGHOUSE_DEBUG              | (False/True)                     | The debugger will be automatically activated in the development environment. For security reasons, it is recommended not to activate it in production. 
LEARNINGHOUSE_RELOAD             | (False/True)                     | The source will be automatically reloaded in the development environment. For security reasons, it is recommended not to activate it in production.

#### Example configuration

You can download [.env.example](https://raw.githubusercontent.com/LearningHouseService/learninghouse/master/core/.env.example) and rename it to `.env`. Inside, you can modify the default configuration values to meet your needs in this file.

## Run the service 

### In the console

Copy the [.env.example](https://raw.githubusercontent.com/LearningHouseService/learninghouse/master/core/.env.example) file to .env and modify it according to your needs.

Then, simply run `learninghouse` to start the service. By default, the service will listen on http://localhost:5000/.

### With docker:

```
docker run --name learninghouse --rm -v brains:/learninghouse/brains -p 5000:5000 -e "TZ=Europe/Berlin" ghcr.io/learninghouseservice/learninghouse:latest
```
## UI
For configuration purposes, there is a small user interface that can be found at http://localhost:5000/ui.

## Security

The service is protected by different authentication and authorization mechanisms. For administration, you can log in via the UI.

### Fallback password
On the first run, the service is set to use the fallback password `learninghouse` for the administrator account. Until this is changed, all other endpoints will be deactivated. 

You can change the password on the initial login screen of the UI.

**Security notice: Unless you use a proxy setup for SSL security of your connection, only use a separate password for your learninghouse.**


### API Key

You can use your administration access for training and prediction endpoints, but we also recommend using an API key mechanism for application access. There are two roles for API key authorization: `user` for the prediction endpoint and `trainer` for the training and prediction endpoints.

You can add more API keys via the UI.

Your API key will only be displayed once and cannot be requested again. So save it for your usage.
If you forget it, you will have to delete this API key and recreate it.

You have to provide this API key for all requests, either as a query parameter `?api_key=YOURSECRETKEY` or as a header field `X-LEARNINGHOUSE-API-KEY: YOURSECRETKEY`.

You can also test the API key by logging in to the UI.

## Brains and Sensors Configuration

### Sensors Configuration

Send data from all sensors to the **learningHouse Service**, especially when training your brains. The service will save all data fields, even if they are not currently used as a `feature`. The service will choose the best feature set each time you train a brain.

In general, sensor data can be divided into two different types. `Numerical data` can be processed directly by your models, while `Categorical data` needs to be preprocessed by the service in order to be used as a `feature`. `Categorical data` can be identified using a simple rule:

- Non-numerical values, or
- Numerical values that can be described using terms.

Here are some examples of categorical data:

- pressure_trend: Values of 'falling', 'rising', 'consistent'
- month_of_year: 1 _('January')_, 2 _('February')_, ...
- weather_condition: 'sunny', 'cloudy'
- switch: 'ON', 'OFF'

To enable the service to use the data from your sensors as `features` for your brain, you need to provide the service with information about the data type. You can add each sensor you want to use via the UI.

For example, add the following sensors:

Name                 | type
---------------------|--------------
azimuth              | numerical
elevation            | numerical
rain_gauge           | numerical
pressure             | numerical
pressure_trend_1h    | categorical
temperature_outside  | numerical
temperature_trend_1h | categorical
light_state          | categorical

### Example brain

The brain determines whether it is dark enough to switch on the light. It utilizes a machine learning algorithm called RandomForestClassifier.

To add a new brain via the UI, use your administration account and provide the following parameters.

Field            | Value
-----------------|------------
Name             | darkness
Typed            | Classifier
Dependent encode | True
Test size        | 0.2
Estimators       | 100
Max depth        | 5

### Configuration Parameters

#### Estimator

The LearningHouse Service can predict values using an estimator. An estimator can be of type `classifier`, which is best suited for categorical outputs, such as true and false. If you want to predict a numerical value, such as the setpoint of a heating equipment, use the type `regressor` instead.

For both types, the **LearningHouse Service** uses a machine learning algorithm called random forest estimation. This algorithm builds a "forest" of decision trees with your `features` and takes the mean of the predictions of all of them to give you the best result. For more details, see the API description of scikit-learn.

| Estimator type | API Reference |
|-----------------|-------------------|
| RandomForestRegressor | https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html#sklearn.ensemble.RandomForestRegressor |
| RandomForestClassifier | https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#sklearn.ensemble.RandomForestClassifier |

You can adjust the number of decision trees by using the `estimators` (default: 100) option. You can also adjust the maximum depth of each tree by using the `max depth` (default: 5) option. Both options are optional. Try resizing these values to optimize the accuracy of your model.

#### Dependent variable

The `dependent` variable is the one that must be included in the training data and is predicted by the trained brain. It is the same as the `name` variable.

The `dependent` variable must be a number. If it is not a number, but a string or boolean (true/false) as shown in the example, set `dependent encode` to yes.

#### Test size

The LearningHouse service only uses a portion of your training data to train the brain. The remaining portion, specified by `test size`, is used to score the accuracy of your brain.

You can specify the `test size` as a percentage using floating point numbers between 0.01 and 0.99, or as an absolute number of data points using integer numbers.

For example, a `test size` of 20% (0.2) should be sufficient to start with.

An accuracy score between 80% and 90% is considered good. Scores below 80% indicate that the brain is underfitted, while scores above 90% indicate that the brain is overfitted. Both cases can result in poor predictions for new data points. You can try adjusting the [`estimator` configuration](#estimator) to improve the score.

Training of the brain will start when there are at least 10 data points.

### Changing configuration via RESTful API

You can also change the configuration of sensors and brains using the API. Please refer to the interactive [API documentation](#api-documentation) when the service is running.

## API Documentation

When the service is running, you can access an interactive API documentation by calling the URL http://localhost:5000/docs.

## Train the brain

To train, send a PUT request to the service:

_You need administration JWT or API key role `trainer` for this request (see [Security](#security))_

```
# URL is http://<host>:5000/api/brain/:name/training
curl --location --request PUT 'http://localhost:5000/api/brain/darkness/training' \
    --header 'Content-Type: application/json' \
    --header 'X-LEARNINGHOUSE-API-KEY: YOURSECRETKEY' \
    --data-raw '{
        "azimuth": 321.4441223144531,
        "elevation": -19.691608428955078,
        "rain_gauge": 0.0,
        "pressure": 971.0,
        "pressure_trend_1h": "falling",
        "temperature_outside": 23.0,
        "temperature_trend_1h": "rising",
        "light_state": false,
        "darkness": true
}'
```

You can send either a field `timestamp` with your dataset containing a UNIX-Timestamp or the service will add this information with its current time. The service generates some further time-relevant fields inside the training dataset that you can also use as `features`. These are `month_of_year`, `day_of_month`, `day_of_week`, `hour_of_day`, and `minute_of_hour`.

If one of your sensors is not working at the moment and therefore not sending a value, the service will add a value using the following rules. For `categorical data`, all categorical columns will be set to zero. For `numerical data`, the mean of all known training set values (see [Test size](#test-size)) for this `feature` will be assumed.

To train the brain with existing data, for example after a service update, use a POST request without data:

_You need an administrator JWT or API key with the role `trainer` for this request (see [Security](#security))._

```
# URL is http://host:5000/api/brain/:name/training
curl --location \
    --header 'X-LEARNINGHOUSE-API-KEY: YOURSECRETKEY' \
    --request POST 'http://localhost:5000/api/brain/darkness/training'
```

To obtain information about a trained brain, use a GET request:

_You will need an administrator JWT or API key with the role of `trainer` or `user` for this request (see [Security](#security))_.

```
# URL is http://host:5000/api/brain/:name/info
curl --location \
    --header 'X-LEARNINGHOUSE-API-KEY: YOURSECRETKEY' \ 
    --request GET 'http://localhost:5000/brain/darkness/info'
```

## Prediction

To predict a new data set with your brain, send a POST request:

_You need an administrator JWT or API key with the role `trainer` or `user` for this request (see [Security](#security))_.

```
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

If one of your sensors used as a `feature` in the brain is not working at the moment and is not sending a value, the service will handle this by using the following rules. For `categorical data`, all categorical columns will be set to zero. For `numerical data`, the mean of all known training set values (see [Test size](#test-size)) for this `feature` will be assumed.
