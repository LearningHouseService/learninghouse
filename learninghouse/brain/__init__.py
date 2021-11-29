from __future__ import annotations

import json
from os import path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import joblib
import pandas as pd
from fastapi import FastAPI, Path, Request
from fastapi.responses import JSONResponse
from learninghouse import ServiceVersions, logger, versions
from learninghouse.brain.api import (BrainErrorMessage, BrainInfo,
                                     BrainTrainingRequest)
from learninghouse.brain.exceptions import (BrainException,
                                            BrainNoConfiguration,
                                            BrainNotActual, BrainNotEnoughData,
                                            BrainNotTrained)
from learninghouse.estimator import EstimatorFactory
from learninghouse.estimator.api import EstimatorConfiguration
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

        self.estimatorcfg: EstimatorConfiguration = EstimatorConfiguration(
            **self._required_param(json_config, 'estimator'))

        self.dataset: DatasetConfiguration = DatasetConfiguration(
            features=self._required_param(json_config, 'features'),
            dependent=self._required_param(json_config, 'dependent')
        )

        self.preprocessing: PreprocessingConfiguration = PreprocessingConfiguration(
            self._required_param(json_config, 'test_size'),
            self._optional_param(json_config, 'dependent_encode', False)
        )

        self.estimator: Optional[Union[RandomForestClassifier,
                                 RandomForestRegressor]] = None
        self.score: Optional[float] = 0.0
        self.versions: ServiceVersions = versions

    @classmethod
    def _load_initial_config(cls, name: str):
        with open(cls.CONFIG_FILE % name, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)

    @classmethod
    def _required_param(cls, json_config: Dict, param_key: str):
        param_value = cls._optional_param(json_config, param_key)

        if param_value is None:
            raise RuntimeError(
                f'Missing required configuration parameter {param_key}')

        return param_value

    @staticmethod
    def _optional_param(json_config: Dict, param_key: str, default=None):
        param_value = default

        if param_key in json_config:
            param_value = json_config[param_key]

        return param_value

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
                estimator: Union[RandomForestClassifier, RandomForestRegressor],
                columns: List[str],
                score: float) -> None:
        self.estimator = estimator
        self.preprocessing.columns = columns
        self.score = score

        joblib.dump(self, self.COMPILED_FILE % self.name)


class BrainTraining():
    TRAINING_FILE = 'brain/training/%s.csv'

    @classmethod
    def request(cls, brain: str, request_data: Optional[Dict[str, Any]] = None):
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
    def train(name: str, data: pd.DataFrame):
        try:
            brain = BrainConfiguration(name)

            if len(data.index) < 10:
                raise BrainNotEnoughData()

            brain, x_train, x_test, y_train, y_test = DatasetPreprocessing.prepare_training(
                brain, data)

            estimator = EstimatorFactory.get_estimator(brain.estimatorcfg)

            columns = x_train.columns

            logger.debug('Train data columns: %s', columns)

            estimator.fit(x_train, y_train)

            if brain.estimatorcfg.typed == 'classifier':
                y_pred = estimator.predict(x_test)
                score = accuracy_score(y_test, y_pred)
            else:
                score = estimator.score(x_test, y_test)

            brain.compile(estimator, columns.to_list(), score)

            return brain.info()
        except FileNotFoundError as exc:
            logger.exception(exc)
            raise BrainNoConfiguration() from exc
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(exc)
            raise BrainException() from exc


class BrainAPI():
    @staticmethod
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
                      BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.description()
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
                     BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.description()
                 })
        async def training_put(name: str, request_data: BrainTrainingRequest):
            return BrainTraining.request(name, request_data.data)

        return app
