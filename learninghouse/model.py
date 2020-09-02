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

from .estimator import EstimatorFactory

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import confusion_matrix, accuracy_score

class ModelConfiguration():
    def __init__(self, name):
        self.name = name

        self.__jsonConfig = self.__loadInitialConfig(name)

        self.estimatorcfg = self.__requiredConfig('estimator')
        self.testsize = self.__requiredConfig('test_size')
        self.features = self.__requiredConfig('features')
        self.dependent = self.__requiredConfig('dependent')

        self.categoricals = self.__optionalConfig('categoricals')
        self.standard_scaled = self.__optionalConfig('standard_scaled')
        if self.standard_scaled is not None:
            self.standard_scaler = StandardScaler()
            self.standard_scaler_fitted = False

        self.dependentEncode = self.__optionalConfig('dependent_encode', False)

        self.estimator = None
        self.columns = None
        self.score = 0.0
        self.confusion = None

    def __loadInitialConfig(self, name):
        with open('models/config/%s.json' % name, 'r') as configFile:
            return json.load(configFile)

    def __requiredConfig(self, param):
        if param in self.__jsonConfig:
            return self.__jsonConfig[param]
        else:
            raise Exception('Missing required param %s' % param)

    def __optionalConfig(self, param, default = None):
        if param in self.__jsonConfig:
            return self.__jsonConfig[param]
        else:
            return default

    def hasCategoricals(self):
        return self.categoricals is not None

    def hasStandardScaled(self):
        return self.standard_scaled is not None

    def hasColumns(self):
        return self.columns is not None

    def configObject(self):
        return {
            'name': self.name,
            'estimator_config': self.estimatorcfg,
            'features': self.features,
            'categoricals': self.categoricals,
            'standard_scaled': self.standard_scaled,
            'dependent': self.dependent,
            'score': self.score,
            'confusion': self.confusion
        }

    def dump(self, estimator, columns, score, confusion):
        self.estimator = estimator
        self.columns = columns
        self.score = score
        self.confusion = confusion

        dump(self, 'models/compiled/%s.pkl' % self.name)

class ModelAPI(Resource):
    @staticmethod
    def makeJSONResponse(data, statusCode = 200, errorCode = None):
        if errorCode is not None:
            data['error'] = errorCode

        resp = jsonify(data)
        resp.status_code = statusCode
        return resp

class ModelTraining(Resource):
    @staticmethod
    def post(model):
        try:
            modelcfg = ModelConfiguration(model)

            filename = 'models/training/%s.csv' % modelcfg.name
            isNew = not path.exists(filename)

            if request.content_length > 0:
                if request.is_json:
                    jsonData = request.get_json()
                    if isNew:
                        df = pd.DataFrame([jsonData])
                    else:
                        df_temp = pd.read_csv(filename)
                        df = df_temp.append([jsonData], ignore_index = True)

                    df.to_csv(filename, sep = ',', index = False)
                else:
                    return ModelAPI.makeJSONResponse({}, 400, 'BAD_REQUEST')
            else:
                if isNew:
                    return ModelAPI.makeJSONResponse({}, 202, 'NOT_ENOUGH_TRAINING_DATA')
                df = pd.read_csv(filename)

            if len(df.index) < 10:
                return ModelAPI.makeJSONResponse({}, 202, 'NOT_ENOUGH_TRAINING_DATA')

            modelcfg, x_train, x_test, y_train, y_test = DatasetPreprocessing.prepareTraining(modelcfg, df)

            estimator = EstimatorFactory.getEstimator(modelcfg.estimatorcfg)
            
            columns = x_train.columns
            
            estimator.fit(x_train, y_train)
            
            y_pred = estimator.predict(x_test)

            cm = confusion_matrix(y_test, y_pred)
            score = accuracy_score(y_test, y_pred)

            modelcfg.dump(estimator, columns, score, cm.tolist())

            return ModelAPI.makeJSONResponse(modelcfg.configObject())
        except FileNotFoundError:
            return ModelAPI.makeJSONResponse({}, 404, 'NO_CONFIGURATION')

class ModelPrediction(Resource):
    modelcfgs = {}

    @staticmethod
    def post(model):
        try: 
            modelcfg = ModelPrediction._loadModelcfg(model)

            json_data = request.get_json(force = True)
            query = pd.DataFrame([json_data])

            x = DatasetPreprocessing.preparePrediction(modelcfg, query)

            prediction = list(map(float, modelcfg.estimator.predict(x)))

            result = {
                'model': modelcfg.configObject(),
                'prediction': prediction[0]
            }

            return ModelAPI.makeJSONResponse(result)

        except BadRequest as e:
            return ModelAPI.makeJSONResponse({}, 400, 'BAD_REQUEST')
        except KeyError as e:
            return ModelAPI.makeJSONResponse({'message': e.args[0]}, 400, 'MISSING_KEY')
        except FileNotFoundError:
            return ModelAPI.makeJSONResponse({}, 404, 'NOT_TRAINED')
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return ModelAPI.makeJSONResponse({}, 500, 'UNKNOWN_ERROR')

    @staticmethod
    def _loadModelcfg(model):
        filename = 'models/compiled/%s.pkl' % model
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
            modelcfg = load('models/compiled/%s.pkl' % model)
            ModelPrediction.modelcfgs[model] = {
                'stamp': stamp,
                'model': modelcfg
            }

        return modelcfg


class DatasetPreprocessing():
    @staticmethod
    def prepareTraining(modelcfg, df):

        if modelcfg.hasCategoricals():
            x = pd.get_dummies(df[modelcfg.features], columns=modelcfg.categoricals)
        else:
            x = df[modelcfg.features]
    
        y = df[modelcfg.dependent]

        if modelcfg.dependentEncode:
            le = LabelEncoder()
            y = le.fit_transform(y)

        x_temp = x.copy()
        for col in x.columns:
            if x[col].isnull().values.any():
                imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
                x_temp[col] = imputer.fit_transform(x[[col]]).ravel()

        x = x_temp

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = modelcfg.testsize, random_state=0)

        if modelcfg.hasStandardScaled():
            if not modelcfg.standard_scaler_fitted:
                x_train[modelcfg.standard_scaled] = modelcfg.standard_scaler.fit_transform(x_train[modelcfg.standard_scaled].values)
                modelcfg.standard_scaler_fitted = True

            x_test[modelcfg.standard_scaled] = modelcfg.standard_scaler.transform(x_test[modelcfg.standard_scaled].values)

        return modelcfg, x_train, x_test, y_train, y_test

    @staticmethod
    def preparePrediction(modelcfg, df):
        if modelcfg.hasCategoricals():
            x = pd.get_dummies(df[modelcfg.features], columns=modelcfg.categoricals)
        else:
            x = df[modelcfg.features]

        x = x.reindex(columns=modelcfg.columns, fill_value=0)
 
        if modelcfg.hasStandardScaled():
            x[modelcfg.standard_scaled] = modelcfg.standard_scaler.transform(x[modelcfg.standard_scaled].values)

        return x