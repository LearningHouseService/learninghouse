from __future__ import annotations

import json
from typing import TYPE_CHECKING, Dict, List, Optional, Union

import joblib
from fastapi import FastAPI, Path, Request
from fastapi.responses import JSONResponse
from learninghouse import ServiceVersions, logger, versions
from learninghouse.brain.api import BrainErrorMessage, BrainInfo
from learninghouse.brain.exceptions import (BrainException, BrainNotActual,
                                            BrainNotTrained)
from learninghouse.estimator.api import EstimatorConfiguration
from learninghouse.preprocessing.api import (DatasetConfiguration,
                                             PreprocessingConfiguration)

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
            self._required_param(json_config, 'features'),
            self._required_param(json_config, 'dependent')
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
        with open(BrainConfiguration.CONFIG_FILE % name, 'r', encoding='utf-8') as config_file:
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
        async def info(name: str):
            brain_config = BrainConfiguration.load_compiled(name)
            return brain_config

        return app
