from __future__ import annotations

import json
from os import path, stat
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import joblib
import pandas as pd
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import accuracy_score

from learninghouse import logger, versions
from learninghouse.core.exceptions import LearningHouseException
from learninghouse.core.exceptions.brain import (BrainNoConfiguration,
                                                 BrainNotActual,
                                                 BrainNotEnoughData,
                                                 BrainNotTrained)
from learninghouse.models import LearningHouseVersions
from learninghouse.models.brain import (BrainEstimatorConfiguration,
                                        BrainEstimatorType, BrainInfo,
                                        BrainPredictionResult)
from learninghouse.models.preprocessing import (DatasetConfiguration,
                                                PreprocessingConfiguration)
from learninghouse.services import sanitize_configuration_filename
from learninghouse.services.preprocessing import DatasetPreprocessing

if TYPE_CHECKING:
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


class BrainConfiguration():
    CONFIG_DIR = 'config'
    CONFIG_EXTENSION = 'json'

    COMPILED_DIR = 'compiled'
    COMPILED_EXTENSION = 'pkl'

    def __init__(self, name: str):
        self.name: str = name

        json_config = self._load_initial_config(name)

        self.estimatorcfg: BrainEstimatorConfiguration = BrainEstimatorConfiguration(
            **self._required_param(json_config, 'estimator'))

        self.dataset: DatasetConfiguration = DatasetConfiguration(
            dependent=self._required_param(json_config, 'dependent')
        )

        self.preprocessing: PreprocessingConfiguration = PreprocessingConfiguration(
            self._required_param(json_config, 'test_size'),
            self._optional_param(json_config, 'dependent_encode', False)
        )

        self._estimator: Optional[Union[RandomForestClassifier,
                                        RandomForestRegressor]] = None
        self.score: Optional[float] = 0.0
        self.versions: LearningHouseVersions = versions

    @classmethod
    def _load_initial_config(cls, name: str) -> Dict[str, Any]:
        filename = sanitize_configuration_filename(
            cls.CONFIG_DIR, name, cls.CONFIG_EXTENSION)
        print(filename)

        with open(filename, 'r', encoding='utf-8') as config_file:
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
            filename = sanitize_configuration_filename(
                cls.COMPILED_DIR, name, cls.COMPILED_EXTENSION)
            brain_config = joblib.load(filename)
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

        filename = sanitize_configuration_filename(
            self.COMPILED_DIR, self.name, self.COMPILED_EXTENSION)

        joblib.dump(self, filename)


class BrainTraining():
    @classmethod
    def request(cls, name: str, request_data: Optional[Dict[str, Any]] = None) -> BrainInfo:
        filename = sanitize_configuration_filename('training', name, 'csv')

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

        return cls.train(name, data)

    @staticmethod
    def train(name: str, data: pd.DataFrame) -> BrainInfo:
        try:
            brain = BrainConfiguration(name)

            if len(data.index) < 10:
                raise BrainNotEnoughData()

            brain, x_train, x_test, y_train, y_test = DatasetPreprocessing.prepare_training(
                brain, data, False)

            estimator = brain.estimator()

            selector = SelectFromModel(estimator)
            selector.fit(x_train, y_train)

            brain.dataset.features = x_train.columns[(
                selector.get_support())].values.tolist()

            brain, x_train, x_test, y_train, y_test = DatasetPreprocessing.prepare_training(
                brain, data, True)

            estimator.fit(x_train, y_train)

            if BrainEstimatorType.CLASSIFIER == brain.estimatorcfg.typed:
                y_pred = estimator.predict(x_test)
                score = accuracy_score(y_test, y_pred)
            else:
                score = estimator.score(x_test, y_test)

            brain.compile(x_train.columns.tolist(), score)

            return brain.info()
        except FileNotFoundError as exc:
            raise BrainNoConfiguration() from exc
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(exc)
            raise LearningHouseException() from exc


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
            raise LearningHouseException() from exc

    @classmethod
    def _load_brain(cls, name: str) -> BrainConfiguration:
        filename = sanitize_configuration_filename(
            BrainConfiguration.COMPILED_DIR, name, BrainConfiguration.COMPILED_EXTENSION)
        stamp = stat(filename).st_mtime

        if not(name in cls.brains and cls.brains[name]['stamp'] == stamp):
            cls.brains[name] = {
                'stamp': stamp,
                'brain': BrainConfiguration.load_compiled(name)
            }

        return cls.brains[name]['brain']
