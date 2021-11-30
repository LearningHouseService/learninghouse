from __future__ import annotations

import json
from os import path, stat
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import joblib
import pandas as pd
from fastapi import FastAPI, Path, Request
from fastapi.responses import JSONResponse
from learninghouse import ServiceVersions, logger, versions
from learninghouse.brain.api import (BrainErrorMessage,
                                     BrainEstimatorConfiguration,
                                     BrainEstimatorType, BrainInfo,
                                     BrainPredictionRequest,
                                     BrainPredictionResult,
                                     BrainTrainingRequest)
from learninghouse.brain.exceptions import (BrainException,
                                            BrainNoConfiguration,
                                            BrainNotActual, BrainNotEnoughData,
                                            BrainNotTrained)
from learninghouse.preprocessing import DatasetPreprocessing
from learninghouse.preprocessing.api import (DatasetConfiguration,
                                             PreprocessingConfiguration)
from sklearn.metrics import accuracy_score

if TYPE_CHECKING:
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


class BrainConfiguration():
    CONFIG_FILE = 'brain/config/%s.json'
    COMPILED_FILE = 'brain/compiled/%s.pkl'

    def __init__(self, name: str):
        self.name: str = name

        json_config = self._load_initial_config(name)

        self.estimatorcfg: BrainEstimatorConfiguration = BrainEstimatorConfiguration(
            **self._required_param(json_config, 'estimator'))

        self.dataset: DatasetConfiguration = DatasetConfiguration(
            features=self._required_param(json_config, 'features'),
            dependent=self._required_param(json_config, 'dependent')
        )

        self.preprocessing: PreprocessingConfiguration = PreprocessingConfiguration(
            self._required_param(json_config, 'test_size'),
            self._optional_param(json_config, 'dependent_encode', False)
        )

        self._estimator: Optional[Union[RandomForestClassifier,
                                        RandomForestRegressor]] = None
        self.score: Optional[float] = 0.0
        self.versions: ServiceVersions = versions

    @classmethod
    def _load_initial_config(cls, name: str) -> Dict[str, Any]:
        with open(cls.CONFIG_FILE % name, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)

    @classmethod
    def _required_param(cls, json_config: Dict[str, Any], param_key: str) -> Any:
        param_value = cls._optional_param(json_config, param_key)

        if param_value is None:
            raise RuntimeError(
                f'Missing required configuration parameter {param_key}')

        return param_value

    @staticmethod
    def _optional_param(json_config: Dict[str, Any], param_key: str, default=None) -> Any | None:
        param_value = default

        if param_key in json_config:
            param_value = json_config[param_key]

        return param_value

    def estimator(self) -> RandomForestClassifier | RandomForestRegressor:
        if self._estimator is None:
            self._estimator = self.estimatorcfg.typed.estimator_class(
                n_estimators=self.estimatorcfg.estimators,
                max_depth=self.estimatorcfg.max_depth,
                random_state=self.estimatorcfg.random_state
            )

        return self._estimator

    def info(self) -> BrainInfo:
        info = BrainInfo(
            name=self.name,
            estimator_config=self.estimatorcfg,
            features=self.dataset.features,
            dependent=self.dataset.dependent,
            dependent_encode=self.preprocessing.dependent_encode,
            score=self.score,
            versions=self.versions
        )

        return info

    @classmethod
    def load_compiled(cls, name: str) -> BrainConfiguration:
        try:
            brain_config = joblib.load(cls.COMPILED_FILE % name)
            if brain_config.versions != versions:
                raise BrainNotActual()

            return brain_config
        except FileNotFoundError as exc:
            raise BrainNotTrained() from exc

    def compile(self,
                columns: List[str],
                score: float) -> None:
        self.preprocessing.columns = columns
        self.score = score

        joblib.dump(self, self.COMPILED_FILE % self.name)


class BrainTraining():
    TRAINING_FILE = 'brain/training/%s.csv'

    @classmethod
    def request(cls, brain: str, request_data: Optional[Dict[str, Any]] = None) -> BrainInfo:
        filename = cls.TRAINING_FILE % brain

        if request_data is None:
            if path.exists(filename):
                data = pd.read_csv(filename)
            else:
                raise BrainNotEnoughData()
        else:
            request_data = DatasetPreprocessing.add_time_information(
                request_data)
            if path.exists(filename):
                data_temp = pd.read_csv(filename)
                data = data_temp.append([request_data], ignore_index=True)
            else:
                data = pd.DataFrame([request_data])

            data.to_csv(filename, sep=',', index=False)

        return cls.train(brain, data)

    @staticmethod
    def train(name: str, data: pd.DataFrame) -> BrainInfo:
        try:
            brain = BrainConfiguration(name)

            if len(data.index) < 10:
                raise BrainNotEnoughData()

            brain, x_train, x_test, y_train, y_test = DatasetPreprocessing.prepare_training(
                brain, data)

            estimator = brain.estimator()

            columns = x_train.columns

            logger.debug('Train data columns: %s', columns)

            estimator.fit(x_train, y_train)

            if BrainEstimatorType.CLASSIFIER == brain.estimatorcfg.typed:
                y_pred = estimator.predict(x_test)
                score = accuracy_score(y_test, y_pred)
            else:
                score = estimator.score(x_test, y_test)

            brain.compile(columns.tolist(), score)

            return brain.info()
        except FileNotFoundError as exc:
            raise BrainNoConfiguration() from exc
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(exc)
            raise BrainException() from exc


class BrainPrediction():
    brains: Dict[str, Dict[str, int | BrainConfiguration]] = {}

    @classmethod
    def prediction(cls, name: str, request_data: Dict[str, Any]):
        try:
            brain = cls._load_brain(name)
            request_data = DatasetPreprocessing.add_time_information(
                request_data)

            data = pd.DataFrame([request_data])
            prepared_data = DatasetPreprocessing.prepare_prediction(
                brain, data)

            prediction = brain.estimator().predict(prepared_data)

            if (brain.preprocessing.dependent_encode
                    and brain.estimatorcfg.typed == BrainEstimatorType.CLASSIFIER):
                prediction = brain.preprocessing.dependent_encoder.inverse_transform(
                    prediction)
                prediction = list(map(bool, prediction))
            else:
                prediction = list(map(float, prediction))

            return BrainPredictionResult(
                brain=brain.info(),
                preprocessed=prepared_data.head(1).to_dict('records')[0],
                prediction=prediction[0]
            )
        except FileNotFoundError as exc:
            raise BrainNotTrained() from exc
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(exc)
            raise BrainException() from exc

    @classmethod
    def _load_brain(cls, name: str) -> BrainConfiguration:
        filename = BrainConfiguration.COMPILED_FILE % name
        stamp = stat(filename).st_mtime

        if not(name in cls.brains and cls.brains[name]['stamp'] == stamp):
            cls.brains[name] = {
                'stamp': stamp,
                'brain': BrainConfiguration.load_compiled(name)
            }

        return cls.brains[name]['brain']


def register(app: FastAPI) -> FastAPI:
    @app.exception_handler(BrainException)
    async def exception_handler(request: Request, exc: BrainException):  # pylint: disable=unused-argument
        return exc.response()

    @app.get('/brain/{name}/info',
             response_model=BrainInfo,
             summary='Retrieve information',
             description='Retrieve all information of a trained brain.',
             tags=['brain'],
             responses={
                 200: {
                     'description': 'Information of the trained brain'
                 },
                 BrainNotTrained.STATUS_CODE: BrainNotTrained.description(),
                 BrainNotActual.STATUS_CODE: BrainNotActual.description(),
                 BrainException.STATUS_CODE: BrainException.description()
             })
    async def info_get(name: str):
        brain_config = BrainConfiguration.load_compiled(name)
        return brain_config.info()

    @app.post('/brain/{name}/training',
              response_model=BrainInfo,
              summary='Train the brain again',
              description='After version updates train the brain with existing data.',
              tags=['brain'],
              responses={
                  200: {
                      'description': 'Information of the trained brain'
                  },
                  BrainNotEnoughData.STATUS_CODE: BrainNotEnoughData.description(),
                  BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.description(),
                  BrainException.STATUS_CODE: BrainException.description()
              })
    async def training_post(name: str):
        return BrainTraining.request(name)

    @app.put('/brain/{name}/training',
             response_model=BrainInfo,
             summary='Train the brain with new data',
             description='Train the brain with additional data.',
             tags=['brain'],
             responses={
                 200: {
                     'description': 'Information of the trained brain'
                 },
                 BrainNotEnoughData.STATUS_CODE: BrainNotEnoughData.description(),
                 BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.description(),
                 BrainException.STATUS_CODE: BrainException.description()
             })
    async def training_put(name: str, request_data: BrainTrainingRequest):
        return BrainTraining.request(name, request_data.data)

    @app.post('/brain/{name}/prediction',
              response_model=BrainPredictionResult,
              summary='Prediction',
              description='Predict a new dataset with given brain.',
              tags=['brain'],
              responses={
                  200: {
                      'description': 'Prediction result'
                  },
                  BrainNotActual.STATUS_CODE: BrainNotActual.description(),
                  BrainNotTrained.STATUS_CODE: BrainNotTrained.description(),
                  BrainException.STATUS_CODE: BrainException.description()
              })
    async def prediction_post(name: str, request_data: BrainPredictionRequest):
        return BrainPrediction.prediction(name, request_data.data)

    return app
