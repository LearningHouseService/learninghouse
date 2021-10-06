# learningHouse Service 
[![License](https://img.shields.io/github/license/LearningHouseService/learninghouse-core)](https://github.com/LearningHouseService/learninghouse-core/blob/master/LICENSE)
[![Build Status](https://img.shields.io/travis/LearningHouseService/learninghouse-core)](https://travis-ci.org/LearningHouseService/learninghouse-core) [![PyPI version](https://img.shields.io/pypi/v/learninghouse.svg)](https://pypi.org/project/learninghouse/) [![Docker version](https://img.shields.io/docker/v/learninghouseservice/learninghouse/latest?label=docker)](https://hub.docker.com/r/learninghouseservice/learninghouse)

![learningHouse Logo](https://raw.githubusercontent.com/LearningHouseService/learninghouse-core/master/artwork/learninghouse_logo.svg)

## Introduction

**learningHouse Service** provides machine learning algorithms based on scikit-learn python library as a RESTful API, with the purpose to give smart home fans an easy possibility to teach their homes.

*Add the moment this project is in a very early state. Please share your ideas what you want to teach your home by opening an [issue](https://github.com/LearningHouseService/learninghouse-core/issues). Really looking forward for your feedback.*

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
mkdir -p models/config
mkdir -p models/training
mkdir -p models/compiled
```

The `config` directory holds the model configuration as json-file.

The directories `training` and `compiled` are used by service to store data.

Training data is stored as csv file, trained models are stored as object dump.

## Configuration of models

Configuration is stored in json format.

### General configuration

In general send data of all sensors to **learningHouse Service** especially when training your models. The service will save all data fields even if they are not used in current model configuration as a `feature`. This will give you the possibility to choose different features later on to improve your model after some training (There will be some service later on to support you with this improvment). 

In general there are two different data types your sensor data can be divided in. `Numerical data` can be processed directly by your models. `Categorical data` has to be preproccesed by the service to be used as a `feature`. `Categorical data` can be identified by a simple rule:

Non numerical values or if you can give each numerical value a term to describe it.

Some examples for categorical data:

- pressure_trend: Values of 'falling', 'rising', 'consistent'
- month_of_year: 1 ('January'), 2 ('Februrary'), ...

To use the data of your sensors as `features` in your models you have to give the service information about the data type. For this put a sensors.json to the directory model/config. List all your sensors and their data type.

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

### Example model

The model decides whether it is so dark that the light has to be switched on. It uses the sun azimuth and sun elevation, the rain gauge and the one hour trend of air pressure. The data of the other senors (pressure, temperature_outside, light_state) isn't used in this example. It use a machine learning algorithm called RandomForestClassifier.

Store a darkness.json in models/config directory with following content:

```
{
    "estimator": {
        "typed": "classifier",
        "estimators": 100, 
        "max_depth": 5
    },
    "features": ["azimuth", "elevation", "rain_gauge", "pressure_trend_1h_falling"],
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

#### Features

The list of `features` is required and holds the names of the sensor data the model uses to take a decision. `Categorical data` as mentioned above will be preprocessed by the service and is divided to one column by each known value. You can use each column as a seperate `feature`. There will be a service later on to help you to choose the set of best features. Meanwhile use the ones you think they maybe have influence on the decision as a first try and start training your house with all sensor data as mentioned above.

#### Dependent variable

The `dependent` variable is the one that have to be in the training data and which is predicted by the trained model.

The `dependent` variable has to be a number. If it is not a number, but a string or boolean (true/false) like in the example. For this set `dependent_encode` to true.

#### Test size

LearningHouse service only uses a part of your training data to train the model. The other part specified by `test_size` will be used to score the accuracy of your model.

Give a percentage by using floating point numbers between 0.01 and 0.99 or a absolute number of data points by using integer numbers.

For the beginning a `test_size` of 20 % (0.2) like the example should be fine.

The accuracy between 80 % and 90 % between is a good score to gain. Below your model is kind of underfitted and above overfitted, which both make it not working well for new data points to be predicted. You can try to change the set of used `features` to gain a better accuracy.

Training of the model will start, when there are at least 10 data points.

## Run service

In the console type `learninghouse` to start the service in development mode. By default the service will run on port 5000. In development mode you will see some log information.

To start service in production mode and specify listen address and port use following command:

```
learninghouse --production --host 127.0.0.1 --port 5001
```

For more or less log output set the verbosity level of the service to DEBUG, INFO (default), WARNING, ERROR or CRITICAL

```
learninghouse --production --host 127.0.0.1 --port 5001 --verbosity DEBUG
```

Run with docker:

```
docker run --name learninghouse --rm -v models:/learninghouse/models -p 5000:5000 learninghouseservice/learninghouse:latest
```

Like above you can adjust the VERBOSITY_LEVEL by adding it as an environment variable.

## Train model

For training send a PUT request to the service:

```
# URL is http://host:5000/training/:modelname
curl --location --request PUT 'http://localhost:5000/training/darkness' \
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

As mentioned above there will be a service feature which helps you to choose the `features` used in your model from time to time to improve the model. For this always send the data of every sensor when train your model. The service will store this values for possible future use.

To train the model with existing data for example after a service update use a POST request without data:

```
# URL is http://host:5000/training/:modelname
curl --location --request POST 'http://localhost:5000/training/darkness'
```

To get the information about a trained model use a GET request:

```
# URL is http://host:5000/info/:modelname
curl --location --request GET 'http://localhost:5000/info/darkness'
```

## Prediction

To predict a new data set with your model send a POST request:

```
# URL is http://host:5000/info/:modelname
curl --location --request POST 'http://localhost:5000/prediction/darkness' \
--header 'Content-Type: application/json' \
--data-raw '{    
    "azimuth": 321.4441223144531,
    "elevation": -19.691608428955078,
    "rain_gauge": 0.0,
    "pressure_trend_1h": "falling"
}'
```

If one of your sensors used as `feature` in the model is not working at the moment and for this not sending a value the service will add this by using following rules. For `categorical data` all categorical columns will be set to zero. For `numerical data` the mean of all known training set values (see Test size) for this `feature` will be assumed.