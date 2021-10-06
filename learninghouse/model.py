#coding: utf-8

import json
from os import path, stat

import numpy as np
import pandas as pd
from flask import jsonify, request
from flask_restful import Resource
from joblib import dump, load
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder, StandardScaler
from werkzeug.exceptions import BadRequest

from . import __version__, logger
from .estimator import EstimatorFactory
from .preprocessing import DatasetPreprocessing


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

    @staticmethod
    def __load_initial_config(name):
        with open(ModelConfiguration.CONFIG_FILE % name, 'r') as config_file:
            return json.load(config_file)

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

    def has_standard_scaled(self):
        return self.standard_scaled is not None

    def has_columns(self):
        return self.columns is not None

    def config_object(self):
        return {
            'name': self.name,
            'estimator_config': self.estimatorcfg,
            'features': self.features,
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
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(exc)
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
                data_temp = pd.read_csv(filename)
                data = data_temp.append([json_data], ignore_index=True)
            else:
                data = pd.DataFrame([json_data])

            data.to_csv(filename, sep=',', index=False)

            response = ModelTraining.train(model, data)
        else:
            response = ModelAPI.make_json_response({}, 400, 'BAD_REQUEST')

        return response

    @staticmethod
    def post(model):
        filename = ModelTraining.TRAINING_FILE % model

        if request.content_length == 0:
            if path.exists(filename):
                data = pd.read_csv(filename)
                response = ModelTraining.train(model, data)
            else:
                response = ModelAPI.make_json_response(
                    {}, 202, 'NOT_ENOUGH_TRAINING_DATA')
        else:
            response = ModelAPI.make_json_response({}, 400, 'BAD_REQUEST')

        return response

    @staticmethod
    def train(model, data):
        try:
            modelcfg = ModelConfiguration(model)

            if len(data.index) < 10:
                return ModelAPI.make_json_response({}, 202, 'NOT_ENOUGH_TRAINING_DATA')

            modelcfg, x_train, x_test, y_train, y_test = DatasetPreprocessing.prepare_training(
                modelcfg, data)

            estimator = EstimatorFactory.get_estimator(modelcfg.estimatorcfg)

            columns = x_train.columns

            logger.debug('Train data columns: %s', columns)

            estimator.fit(x_train, y_train)

            y_pred = estimator.predict(x_test)

            confusion = confusion_matrix(y_test, y_pred)
            score = accuracy_score(y_test, y_pred)

            modelcfg.dump(estimator, columns, score, confusion.tolist())

            return ModelAPI.make_json_response(modelcfg.config_object())
        except FileNotFoundError:
            return ModelAPI.make_json_response({}, 404, 'NO_CONFIGURATION')
        except KeyError as exc:
            return ModelAPI.make_json_response({'message': exc.args[0]}, 400, 'MISSING_KEY')
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(exc)
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

            prepared_query = DatasetPreprocessing.prepare_prediction(
                modelcfg, query)

            logger.debug('Predict data columns: %s', prepared_query.columns)

            prediction = modelcfg.estimator.predict(prepared_query)

            if modelcfg.dependent_encode:
                prediction = modelcfg.dependent_encoder.inverse_transform(
                    prediction)
                prediction = list(map(bool, prediction))
            else:
                prediction = list(map(float, prediction))

            result = {
                'model': modelcfg.config_object(),
                'preprocessed_query': prepared_query.head(1).to_dict('records'),
                'prediction': prediction[0]
            }

            return ModelAPI.make_json_response(result)
        except BadRequest:
            return ModelAPI.make_json_response({}, 400, 'BAD_REQUEST')
        except KeyError as exc:
            return ModelAPI.make_json_response({'message': exc.args[0]}, 400, 'MISSING_KEY')
        except FileNotFoundError:
            return ModelAPI.make_json_response({}, 404, 'NOT_TRAINED')
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(exc)
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
