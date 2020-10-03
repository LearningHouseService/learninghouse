# learningHouse Service 
[![License](https://img.shields.io/github/license/LearningHouseService/learninghouse-core)](https://github.com/LearningHouseService/learninghouse-core/blob/master/LICENSE)
[![Build Status](https://img.shields.io/travis/LearningHouseService/learninghouse-core)](https://travis-ci.org/LearningHouseService/learninghouse-core) [![PyPI version](https://img.shields.io/pypi/v/learninghouse.svg)](https://pypi.org/project/learninghouse/) 

![learningHouse Logo](https://raw.githubusercontent.com/LearningHouseService/learninghouse-core/master/artwork/learninghouse_logo.svg)

## Introduction

**learningHouse Service** provides machine learning algorithms based on scikit-learn python library as a RESTful API, with the purpose to give smart home fans an easy possibility to teach their homes.

*Add the moment this project is in a very early state. Please share your ideas what you want to teach your home by opening an issue. Really looking forward for your feedback.*

## Installation

Install and update using pip.
```
pip install -U learninghouse
```

Install and update using docker
```
docker pull learninghouseservice/learninghouse
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

### Example model

The model decides whether it is so dark that the light has to be switched on. It uses the sun azimuth and sun elevation, the rain gauge and the one hour trend of air pressure. It use a machine learning algorithm called RandomForestClassifier.

Store a darkness.json in models/config directory with following content:

```
{
    "estimator": {
        "class": "RandomForestClassifier",
        "options": {
            "n_estimators": 100, 
            "random_state": 0
        }
    },
    "features": ["azimuth", "elevation", "rain_gauge", "pressure_trend_1h"],
    "categoricals": ["pressure_trend_1h"],
    "dependent": "darkness",
    "dependent_encode": true,
    "test_size": 0.2
}
```

### Configuration parameter

#### Estimator

First of all we choose an `estimator` with one of scikit-learn estimator classes and configure it with the options you can find at API description. 

At the moment learningHouse service supports the following estimators from scikit-learn:

| Estimator class | API Reference for options |
|-----------------|-------------------|
| DecisionTreeClassifier | https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier |
| RandomForestClassifier | https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#sklearn.ensemble.RandomForestClassifier |

#### Features

The list of `features` is required and holds the names of the sensor data the model uses to take a decision

#### Categoricals

To work correctly all `features` which contain `categorical` data need to be encoded to make model work correct. Give a list of those features which contains such categorical data.

At the example the `feature` pressure_trend_1h is a categorical feature with the categories rising, constant and falling. 

*As a rule of thumb you can assume, that all string values are categoricals.*

#### Dependent variable

The `dependent` variable is the one that have to be in the training data and which is predicted by the model.

The `dependent` variable has to be encoded to a number. If it is not a number, but a string or boolean (true/false) like in the example. For this set `dependent_encode` to true.

#### Test size

LearningHouse service only uses a part of your training data to train the model. The other part specified by `test_size` will be used to score the accuracy of your model.

Give a percentage by using floating point numbers between 0.01 and 0.99 or a absolute number of data points by using integer numbers.

For the beginning a `test_size` of 20 % (0.2) like the example should be fine.

The accuracy between 80 % and 90 % between is a good score to gain. Below your model is kind of underfitted and above overfitted, which make it not working well for new data points to be predicted.

Training of the model will start, when there are at least 10 data points.

## Run service

In the console type `learninghouse` to start the service in development mode. By default the service will run on port 5000. In development mode you will see some log information.

To start service in production mode and specify listen address and port use following command:

```
learninghouse --production --host 127.0.0.1 --port 5001
```

*Service in production mode is not logging anything yet*

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
    "pressure_trend_1h": "falling",
    "darkness": true
}'
```

You can send either a field `timestamp` with your dataset containing a UNIX-Timestamp or the service will add this information with its current time. The service generate some further time relevant fields inside the training dataset you can although use as `features`.

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