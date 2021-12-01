# learningHouse Service 
[![License](https://img.shields.io/github/license/LearningHouseService/learninghouse-core)](https://github.com/LearningHouseService/learninghouse-core/blob/master/LICENSE) [![Release](https://img.shields.io/github/v/release/LearningHouseService/learninghouse-core)](https://github.com/LearningHouseService/learninghouse-core/releases/latest) [![Build Status](https://img.shields.io/github/workflow/status/LearningHouseService/learninghouse-core/build-project/master)](https://github.com/LearningHouseService/learninghouse-core/actions/workflows/build_project.yml) [![PyPI version](https://img.shields.io/pypi/v/learninghouse.svg)](https://pypi.org/project/learninghouse/) [![Build Status Docker](https://img.shields.io/github/workflow/status/LearningHouseService/learninghouse-docker/build-project/master?label=build-docker)](https://github.com/LearningHouseService/learninghouse-docker/actions/workflows/build_project.yml) [![Docker version](https://img.shields.io/docker/v/learninghouseservice/learninghouse/latest?label=docker)](https://hub.docker.com/r/learninghouseservice/learninghouse) [![Docker image size](https://img.shields.io/docker/image-size/learninghouseservice/learninghouse/latest)](https://hub.docker.com/r/learninghouseservice/learninghouse)

![learningHouse Logo](https://raw.githubusercontent.com/LearningHouseService/learninghouse-core/master/artwork/learninghouse_logo.svg)

## Introduction

**learningHouse Service** provides machine learning algorithms based on scikit-learn python library as a RESTful API, with the purpose to give smart home fans an easy possibility to teach their homes.

*At this moment the project is in an early state. Please share your ideas what you want to teach your home by opening an [issue](https://github.com/LearningHouseService/learninghouse-core/issues). Really looking forward for your feedback.*

## Installation

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
mkdir -p brain/config
mkdir -p brain/training
mkdir -p brain/compiled
```

The `config` directory holds the model configuration as json-file. The models are the brains of your learning house.

The directories `training` and `compiled` are used by service to store data.

Training data is stored as csv file, trained brains are stored as object dump.

## Configuration of brains

Configuration is stored in json format.

### General configuration

In general send data of all sensors to **learningHouse Service** especially when training your brains. The service will save all data fields even if they are not used in current brain configuration as a `feature`. The service will choose the best feature set each time you train a brain.

In general there are two different data types your sensor data can be divided in. `Numerical data` can be processed directly by your models. `Categorical data` has to be preproccesed by the service to be used as a `feature`. `Categorical data` can be identified by a simple rule:

Non numerical values or if you can give each numerical value a term to describe it.

Some examples for categorical data:

- pressure_trend: Values of 'falling', 'rising', 'consistent'
- month_of_year: 1 ('January'), 2 ('Februrary'), ...

To enable the servie to use the data of your sensors as `features` for your brain, you have to give the service information about the data type. For this put a sensors.json to the directory brain/config. List all your sensors and their data type.

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

The brain decides whether it is so dark that the light has to be switched on. It uses the sun azimuth and sun elevation, the rain gauge and the one hour trend of air pressure. The data of the other senors (pressure, temperature_outside, light_state) isn't used in this example. It use a machine learning algorithm called RandomForestClassifier.

Store a darkness.json in brain/config directory with following content:

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

The accuracy between 80 % and 90 % between is a good score to gain. Below your brain is kind of underfitted and above overfitted, which both make it not working well for new data points to be predicted. You can try to change the `estimator` configuration (see above) to gain a better score

Training of the brain will start, when there are at least 10 data points.

## Run service

In the console type `learninghouse` to start the service in development mode. By default the service will run on port 5000. In development mode you will see some log information.

To start service in production mode and specify listen address and port use following command:

```
learninghouse --production --host 127.0.0.1 --port 5000
```

For more or less log output set the verbosity level of the service to DEBUG, INFO (default), WARNING, ERROR or CRITICAL

```
learninghouse --production --host 127.0.0.1 --port 5000 --verbosity DEBUG
```

Run with docker:

```
docker run --name learninghouse --rm -v brain:/learninghouse/brain -p 5000:5000 learninghouseservice/learninghouse:latest
```

Like above you can adjust the VERBOSITY_LEVEL by adding it as an environment variable.

## API Documentation

When the service is running, you can reach an interactive API documentation by calling url http://<host>:5000/docs

## Train brain

For training send a PUT request to the service:

```
# URL is http://<host>:5000/brain/:name/training
curl --location --request PUT 'http://localhost:5000/brain/darkness/training' \
--header 'Content-Type: application/json' \
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

If one of your sensors is not working at the moment and for this not sending a value the service will add a value by using the following rules. For `categorical data` all categorical columns will be set to zero. For `numerical data` the mean of all known training set values (see Test size) for this `feature` will be assumed.

To train the brain with existing data for example after a service update use a POST request without data:

```
# URL is http://host:5000/brain/:name/training
curl --location --request POST 'http://localhost:5000/brain/darkness/training'
```

To get the information about a trained brain use a GET request:

```
# URL is http://host:5000/brain/:name/info
curl --location --request GET 'http://localhost:5000/brain/darkness/info'
```

## Prediction

To predict a new data set with your brain send a POST request:

```
# URL is http://host:5000/brain/:name/prediction
curl --location --request POST 'http://localhost:5000/brain/darkness/prediction' \
--header 'Content-Type: application/json' \
--data-raw '{    
    "azimuth": 321.4441223144531,
    "elevation": -19.691608428955078,
    "rain_gauge": 0.0,
    "pressure_trend_1h": "falling"
}'
```

If one of your sensors used as `feature` in the brain is not working at the moment and for this not sending a value the service will add this by using following rules. For `categorical data` all categorical columns will be set to zero. For `numerical data` the mean of all known training set values (see Test size) for this `feature` will be assumed.
