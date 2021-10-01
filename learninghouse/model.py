#coding: utf-8

from flask import request, jsonify
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from joblib import load, dump

import json

from os import path, stat
import sys

import time

import pandas as pd
import numpy as np

from . import __version__, logger

from .preprocessing import DatasetPreprocessing
from .estimator import EstimatorFactory


from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import confusion_matrix, accuracy_score


class ModelConfiguration():
    CONFIG_FILE = 'models/config/%s.json'
    COMPILED_FILE = 'models/compiled/%s.pkl'

    def __init__(self, name):
        self.name = name

        self.__json_config = self.__load_initial_config(name)

        self.estimatorcfg = self.__required_config('estimator')
        self.testsize = self.__required_config('test_size')
        self.features = self.__required_config('features')
        self.dependent = self.__required_config('dependent')

        self.categoricals = self.__optional_config('categoricals')
        if self.categoricals is None:
            self.non_categoricals = self.features
        else:
            self.non_categoricals = [
                item for item in self.features if item not in set(self.categoricals)]

        self.imputer = SimpleImputer(missing_values=np.nan, strategy='mean')

        self.standard_scaled = self.__optional_config('standard_scaled')
        if self.standard_scaled is not None:
            self.standard_scaler = StandardScaler()
            self.standard_scaler_fitted = False

        self.dependent_encode = self.__optional_config(
            'dependent_encode', False)
        if self.dependent_encode:
            self.dependent_encoder = LabelEncoder()

        self.estimator = None
        self.columns = None
        self.score = 0.0
        self.confusion = None
        self.version = __version__

    def __load_initial_config(self, name):
        with open(ModelConfiguration.CONFIG_FILE % name, 'r') as configFile:
            return json.load(configFile)

    def __required_config(self, param):
        if param in self.__json_config:
            return self.__json_config[param]
        else:
            raise RuntimeError('Missing required param %s' % param)

    def __optional_config(self, param, default=None):
        if param in self.__json_config:
            return self.__json_config[param]
        else:
            return default

    def has_categoricals(self):
        return self.categoricals is not None

    def has_standard_scaled(self):
        return self.standard_scaled is not None

    def has_columns(self):
        return self.columns is not None

    def config_object(self):
        return {
            'name': self.name,
            'estimator_config': self.estimatorcfg,
            'features': self.features,
            'categoricals': self.categoricals,
            'standard_scaled': self.standard_scaled,
            'dependent_encode': self.dependent_encode,
            'dependent': self.dependent,
            'score': self.score,
            'confusion': self.confusion,
            'version': {
                'model': self.version,
                'service': __version__
            }
        }

    def dump(self, estimator, columns, score, confusion):
        self.estimator = estimator
        self.columns = columns
        self.score = score
        self.confusion = confusion

        dump(self, ModelConfiguration.COMPILED_FILE % self.name)


class ModelAPI(Resource):
    @staticmethod
    def make_json_response(data, status_code=200, error_code=None):
        if error_code is not None:
            data['error'] = error_code

        resp = jsonify(data)
        resp.status_code = status_code
        return resp

    @staticmethod
    def get(model):
        try:
            modelcfg = load(ModelConfiguration.COMPILED_FILE % model)
            return ModelAPI.make_json_response(modelcfg.config_object())
        except FileNotFoundError:
            return ModelAPI.make_json_response({}, 404, 'NOT_TRAINED')
        except Exception as e:
            logger.error(e)
            return ModelAPI.make_json_response({}, 500, 'UNKNOWN_ERROR')


class ModelTraining(Resource):
    TRAINING_FILE = 'models/training/%s.csv'

    @staticmethod
    def put(model):
        if request.content_length > 0 and request.is_json:
            filename = ModelTraining.TRAINING_FILE % model
            json_data = request.get_json()
            json_data = DatasetPreprocessing.add_time_information(json_data)
            if path.exists(filename):
                df_temp = pd.read_csv(filename)
                df = df_temp.append([json_data], ignore_index=True)
            else:
                df = pd.DataFrame([json_data])

            df.to_csv(filename, sep=',', index=False)

            return ModelTraining.train(model, df)
        else:
            return ModelAPI.make_json_response({}, 400, 'BAD_REQUEST')

    @staticmethod
    def post(model):
        filename = ModelTraining.TRAINING_FILE % model

        if request.content_length == 0:
            if path.exists(filename):
                df = pd.read_csv(filename)
                return ModelTraining.train(model, df)
            else:
                return ModelAPI.make_json_response({}, 202, 'NOT_ENOUGH_TRAINING_DATA')
        else:
            return ModelAPI.make_json_response({}, 400, 'BAD_REQUEST')

    @staticmethod
    def train(model, df):
        try:
            modelcfg = ModelConfiguration(model)

            if len(df.index) < 10:
                return ModelAPI.make_json_response({}, 202, 'NOT_ENOUGH_TRAINING_DATA')

            modelcfg, x_train, x_test, y_train, y_test = DatasetPreprocessing.prepare_training(
                modelcfg, df)

            estimator = EstimatorFactory.get_estimator(modelcfg.estimatorcfg)

            columns = x_train.columns

            estimator.fit(x_train, y_train)

            y_pred = estimator.predict(x_test)

            cm = confusion_matrix(y_test, y_pred)
            score = accuracy_score(y_test, y_pred)

            modelcfg.dump(estimator, columns, score, cm.tolist())

            return ModelAPI.make_json_response(modelcfg.config_object())
        except FileNotFoundError:
            return ModelAPI.make_json_response({}, 404, 'NO_CONFIGURATION')
        except KeyError as e:
            return ModelAPI.make_json_response({'message': e.args[0]}, 400, 'MISSING_KEY')
        except Exception as e:
            logger.error(e)
            return ModelAPI.make_json_response({}, 500, 'UNKNOWN_ERROR')


class ModelPrediction(Resource):
    modelcfgs = {}

    @staticmethod
    def post(model):
        try:
            modelcfg = ModelPrediction._load_modelcfg(model)

            json_data = request.get_json(force=True)
            json_data = DatasetPreprocessing.add_time_information(json_data)
            query = pd.DataFrame([json_data])

            x = DatasetPreprocessing.prepare_prediction(modelcfg, query)

            prediction = modelcfg.estimator.predict(x)

            if modelcfg.dependent_encode:
                prediction = modelcfg.dependent_encoder.inverse_transform(
                    prediction)
                prediction = list(map(bool, prediction))
            else:
                prediction = list(map(float, prediction))

            result = {
                'model': modelcfg.config_object(),
                'prediction': prediction[0]
            }

            return ModelAPI.make_json_response(result)
        except BadRequest as e:
            return ModelAPI.make_json_response({}, 400, 'BAD_REQUEST')
        except KeyError as e:
            return ModelAPI.make_json_response({'message': e.args[0]}, 400, 'MISSING_KEY')
        except FileNotFoundError:
            return ModelAPI.make_json_response({}, 404, 'NOT_TRAINED')
        except Exception as e:
            logger.error(e)
            return ModelAPI.make_json_response({}, 500, 'UNKNOWN_ERROR')

    @staticmethod
    def _load_modelcfg(model):
        filename = ModelConfiguration.COMPILED_FILE % model
        stamp = stat(filename).st_mtime

        if model in ModelPrediction.modelcfgs:
            if ModelPrediction.modelcfgs[model]['stamp'] == stamp:
                modelcfg = ModelPrediction.modelcfgs[model]['model']
            else:
                modelcfg = load(filename)
                ModelPrediction.modelcfgs[model] = {
                    'stamp': stamp,
                    'model': modelcfg
                }
        else:
            modelcfg = load(filename)
            ModelPrediction.modelcfgs[model] = {
                'stamp': stamp,
                'model': modelcfg
            }

        return modelcfg
