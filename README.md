# learningHouse Service 
[![License](https://img.shields.io/github/license/LearningHouseService/learninghouse-core)](https://github.com/LearningHouseService/learninghouse-core/blob/master/LICENSE) [![Release](https://img.shields.io/github/v/release/LearningHouseService/learninghouse-core)](https://github.com/LearningHouseService/learninghouse-core/releases/latest) [![Build Status](https://img.shields.io/github/workflow/status/LearningHouseService/learninghouse-core/build-project/master)](https://github.com/LearningHouseService/learninghouse-core/actions/workflows/build_project.yml) [![PyPI version](https://img.shields.io/pypi/v/learninghouse.svg)](https://pypi.org/project/learninghouse/) [![Build Status Docker](https://img.shields.io/github/workflow/status/LearningHouseService/learninghouse-docker/build-project/master?label=build-docker)](https://github.com/LearningHouseService/learninghouse-docker/actions/workflows/build_project.yml) [![Docker version](https://img.shields.io/docker/v/learninghouseservice/learninghouse/latest?label=docker)](https://hub.docker.com/r/learninghouseservice/learninghouse) [![Docker image size](https://img.shields.io/docker/image-size/learninghouseservice/learninghouse/latest)](https://hub.docker.com/r/learninghouseservice/learninghouse) [![Discord Chat](https://img.shields.io/discord/997393653758697482)](https://discord.gg/U9axHEYqqB)

![learningHouse Logo](https://raw.githubusercontent.com/LearningHouseService/learninghouse-core/master/artwork/learninghouse_logo.svg)

## Introduction

**learningHouse Service** provides machine learning algorithms based on scikit-learn python library as a RESTful API, with the purpose to give smart home fans an easy possibility to teach their homes.

*At this moment the project is in an early state. Please share your ideas what you want to teach your home by opening an [issue](https://github.com/LearningHouseService/learninghouse-core/issues). Really looking forward for your feedback.*

## Contact.

If you have any questions please get in contact with us on discord.

[![Discord Banner](https://discordapp.com/api/guilds/997393653758697482/widget.png?style=banner2)](https://discord.gg/U9axHEYqqB)

## Installation and configuration

Install and update using pip.
```
pip install -U learninghouse
```

Install and update using docker
```
docker pull learninghouseservice/learninghouse:latest
```

### Prepare configuration directory
```
mkdir -p brains
```

The `brains` directory holds the model configuration as json-file. The models are the brains of your learning house.

There will be one subdirectory per brain, where all files relevant for a brain will be stored.
The brain subdirectory needs a `config.json` holding the basic configuration. The service will store a `training_data.csv` holding
all data of your sensors and an object dump of the trained model to a file called `trained.pkl`.

### Service configuration

The service is configured by environment variables. Following options can be set:

Environment Variable           | default (production/development) | description                                            
------------------------------ | -------------------------------- | ------------------------------------------------------ 
LEARNINGHOUSE_ENVIRONMENT      | production                       | Choose environment default settings production or development. 
LEARNINGHOUSE_HOST             | 127.0.0.1                        | Set address the service should bind. (use 0.0.0.0 for all available)
LEARNINGHOUSE_PORT             | 5000                             | Set the port the service should listen.
LEARNINGHOUSE_CONFIG_DIRECTORY | ./brains                         | Define directory where all configuration data goes
LEARNINGHOUSE_OPENAPI_FILE     | /learninghouse_api.json          | File url path to OpenAPI json file
LEARNINGHOUSE_DOCS_URL         | /docs                            | Define url path for interactive [API documentation](#api-documentation). If you set to empty the documentation will be disabled.
LEARNINGHOUSE_API_KEY_REQUIRED | (True/False)                     | Activate [API Key authorization](#security)
LEARNINGHOUSE_API_KEY          | _Generated on startup_           | If [API key authorization](#security) is activated you can specify the required API key. If not defined there is a new own generated on each service restart. The used API key will be logged at service startup.
LEARNINGHOUSE_API_KEY_ADMIN    | _None_                           | To activate [configuration endpoints](#change-configuration-via-restful-api) you have to set an administration API key. You will get a warning if not set.
LEARNINGHOUSE_LOGGING_LEVEL    | INFO                             | Set logging level to DEBUG, INFO, WARNING, ERROR, CRITICAL
LEARNINGHOUSE_DEBUG            | (False/True)                     | Debugger will be automatically activated in development environment. For security reasons it is recommended not to activate in production. 
LEARNINGHOUSE_RELOAD           | (False/True)                     | Reload of source will be automatically activated in development environment. For security reasons it is recommended not to activate in production. 

#### Example

You can download [.env.example](https://raw.githubusercontent.com/LearningHouseService/learninghouse-core/master/.env.example) 
and rename it to `.env`. Inside you can modify default configuration values to your needs in this file.


### Sensors configuration

Send data of all sensors to **learningHouse Service** especially when training your brains. The service will save all data fields even if they are not used as a `feature` at the moment. The service will choose the best feature set each time you train a brain.

In general there are two different data types your sensor data can be divided in. `Numerical data` can be processed directly by your models. `Categorical data` has to be preproccesed by the service to be used as a `feature`. `Categorical data` can be identified by a simple rule:

**Non numerical values or if you can give each numerical value a term to describe it.**

Some examples for categorical data:

- pressure_trend: Values of 'falling', 'rising', 'consistent'
- month_of_year: 1 _('January')_, 2 _('Februrary')_, ...
- weather_condition: 'sunny', 'cloudy'
- switch: 'ON', 'OFF'

To enable the service to use the data of your sensors as `features` for your brain, you have to give the service information about the data type. For this put a `sensors.json` to the directory brains. List all your sensors and their data type.

Example content of sensors.json:

```
{
    "azimuth": "numerical",
    "elevation": "numerical",
    "rain_gauge": "numerical",
    "pressure": "numerical",
    "pressure_trend_1h": "categorical",
    "temperature_outside": "numerical",
    "temperature_trend_1h": "categorical",
    "light_state": "categorical"
}
```



### Example brain

The brain decides whether it is so dark that the light has to be switched on. It uses a machine learning algorithm called RandomForestClassifier.

Store a config.json in brains/darkness subdirectory with following content:

```
{
    "estimator": {
        "typed": "classifier",
        "estimators": 100, 
        "max_depth": 5
    }
    "dependent": "darkness",
    "dependent_encode": true,
    "test_size": 0.2
}
```

### Configuration parameter

#### Estimator

**LearningHouse Service** can predict values using an estimator. An estimator can be of type `classifier` which fits best for your needs if you have somekind of categorical output like in the example true and false. If you want to predict a numerical value for example the setpoint of an heating equipment use the type `regressor` instead.

For both types **learningHouse Service** uses a machine learning algorithm called random forest estimation. This algorithm builds a "forest" of decision trees with your `features` and takes the mean of the prediction of all of them to give you a best result. For more details see the API description of scikit-learn:

| Estimator type | API Reference |
|-----------------|-------------------|
| RandomForestRegressor | https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html#sklearn.ensemble.RandomForestRegressor |
| RandomForestClassifier | https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#sklearn.ensemble.RandomForestClassifier |

You can adjust the amount of decision trees by using `estimators` (default: 100) option. And the maximum depth of each tree by using `max_depth` (default: 5) option. Both options are optional. Try to resize this value to optimize the accuracy of your model.


#### Dependent variable

The `dependent` variable is the one that have to be in the training data and which is predicted by the trained brain.

The `dependent` variable has to be a number. If it is not a number, but a string or boolean (true/false) like in the example. For this set `dependent_encode` to true.

#### Test size

LearningHouse service only uses a part of your training data to train the brain. The other part specified by `test_size` will be used to score the accuracy of your brain.

Give a percentage by using floating point numbers between 0.01 and 0.99 or a absolute number of data points by using integer numbers.

For the beginning a `test_size` of 20 % (0.2) like the example should be fine.

The accuracy between 80 % and 90 % between is a good score to gain. Below your brain is kind of underfitted and above overfitted, which both make it not working well for new data points to be predicted. You can try to change the [`estimator` configuration](#estimator) to gain a better score

Training of the brain will start, when there are at least 10 data points.

### Change configuration via RESTful API

You can change the configuration of sensors and brains although via the API. Visit the interactive [API documentation](#api-documentation) when the service is running.

The configuration endpoints are always protected by an API key (see [Security](#security)). If required admin API key is not set in [service configuration](#service-configuration) the endpoints will be deactivated.

## Run service 

### In console

Copy the [.env.example](https://raw.githubusercontent.com/LearningHouseService/learninghouse-core/master/.env.example)
to .env and modify it to your needs.

Then just run `learninghouse` to run the service. By default the service will listen to http://localhost:5000/

### With docker:

```
docker run --name learninghouse --rm -v brains:/learninghouse/brains -p 5000:5000 learninghouseservice/learninghouse:latest
```

## API Documentation

When the service is running, you can reach an interactive API documentation by calling url http://localhost:5000/docs

## Security

In production mode the service will be protected by an API key mechanism. You can either configure a stable API Key (see [Service Configuration](#service-configuration)) or the service will generate one on each startup. The current used API key will be logged on startup. If API key authorization is activated you have to give an valid API Key for each request either as query parameter `?api_key=YOURSECRETKEY` or as header field `X-LEARNINGHOUSE-API-KEY: YOURSECRETKEY`.

There are two different API keys for user of brain endpoints and [configuration endpoints](#change-configuration-via-restful-api) (see [Service Configuration](#service-configuration)).  

## Train brain

For training send a PUT request to the service:

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

You can send either a field `timestamp` with your dataset containing a UNIX-Timestamp or the service will add this information with its current time. The service generate some further time relevant fields inside the training dataset you can although use as `features`. These are `month_of_year`, `day_of_month`, `day_of_week`, `hour_of_day` and `minute_of_hour`

If one of your sensors is not working at the moment and for this not sending a value the service will add a value by using the following rules. For `categorical data` all categorical columns will be set to zero. For `numerical data` the mean of all known training set values (see [Test size](#test-size)) for this `feature` will be assumed.

To train the brain with existing data for example after a service update use a POST request without data:

```
# URL is http://host:5000/api/brain/:name/training
curl --location \
    --header 'X-LEARNINGHOUSE-API-KEY: YOURSECRETKEY' \
    --request POST 'http://localhost:5000/api/brain/darkness/training'
```

To get the information about a trained brain use a GET request:

```
# URL is http://host:5000/api/brain/:name/info
curl --location \
    --header 'X-LEARNINGHOUSE-API-KEY: YOURSECRETKEY' \ 
    --request GET 'http://localhost:5000/brain/darkness/info'
```

## Prediction

To predict a new data set with your brain send a POST request:

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

If one of your sensors used as `feature` in the brain is not working at the moment and for this not sending a value the service will add this by using following rules. For `categorical data` all categorical columns will be set to zero. For `numerical data` the mean of all known training set values (see [Test size](#test-size)) for this `feature` will be assumed.
