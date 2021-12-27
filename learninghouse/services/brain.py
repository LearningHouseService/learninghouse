from __future__ import annotations

from datetime import datetime
import json
from os import path, stat
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import joblib
import pandas as pd
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import accuracy_score

from learninghouse import versions
from learninghouse.api.errors import LearningHouseException
from learninghouse.api.errors.brain import (BrainNoConfiguration,
                                            BrainNotActual,
                                            BrainNotEnoughData,
                                            BrainNotTrained)
from learninghouse.core.logging import logger
from learninghouse.models import LearningHouseVersions
from learninghouse.models.brain import (BrainEstimatorConfiguration,
                                        BrainEstimatorType, BrainInfo,
                                        BrainPredictionResult)
from learninghouse.models.preprocessing import DatasetConfiguration
from learninghouse.services import sanitize_configuration_filename
from learninghouse.services.preprocessing import DatasetPreprocessing

if TYPE_CHECKING:
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


class Brain():
    CONFIG_FILE = 'config.json'
    TRAINED_FILE = 'trained.pkl'
    INFO_FILE = 'info.json'

    def __init__(self, name: str):
        self.name: str = name

        json_config = self._load_initial_config(name)

        self.estimatorcfg: BrainEstimatorConfiguration = BrainEstimatorConfiguration(
            **self._required_param(json_config, 'estimator'))

        self.dataset: DatasetConfiguration = DatasetConfiguration(
            dependent=self._required_param(json_config, 'dependent'),
            testsize=self._required_param(json_config, 'test_size'),
            dependent_encode=self._optional_param(
                json_config, 'dependent_encode', False),

        )

        self._estimator: Optional[Union[RandomForestClassifier,
                                        RandomForestRegressor]] = None
        self.score: Optional[float] = 0.0

        self.versions: LearningHouseVersions = versions

        self.trained_at: Optional[datetime] = None

    @classmethod
    def _load_initial_config(cls, name: str) -> Dict[str, Any]:
        filename = sanitize_configuration_filename(name, cls.CONFIG_FILE)

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

    @property
    def info(self) -> BrainInfo:
        info = BrainInfo(
            name=self.name,
            estimator_config=self.estimatorcfg,
            features=self.dataset.features,
            dependent=self.dataset.dependent,
            dependent_encode=self.dataset.dependent_encode,
            score=self.score,
            trained_at=self.trained_at,
            versions=self.versions
        )

        return info

    @classmethod
    def load_trained(cls, name: str) -> Brain:
        try:
            filename = sanitize_configuration_filename(
                name, cls.TRAINED_FILE)
            brain_config = joblib.load(filename)
            if brain_config.versions != versions:
                logger.warning(
                    f'Trained brain {name} is not actual. Versions: {brain_config.versions}')
                raise BrainNotActual(name, brain_config.versions)

            return brain_config
        except FileNotFoundError as exc:
            raise BrainNotTrained(name) from exc

    def store_trained(self,
                      columns: List[str],
                      score: float) -> None:
        self.dataset.columns = columns
        self.score = score
        self.trained_at = datetime.now()

        filename = sanitize_configuration_filename(
            self.name, self.TRAINED_FILE)

        joblib.dump(self, filename)

        filename = sanitize_configuration_filename(self.name, self.INFO_FILE)
        with open(filename, 'w', encoding='utf-8') as infofile:
            infofile.write(self.info.json(indent=4))


class BrainTraining():
    TRAINING_DATA_FILE = 'training_data.csv'

    @classmethod
    def request(cls, name: str, request_data: Optional[Dict[str, Any]] = None) -> BrainInfo:
        filename = sanitize_configuration_filename(
            name, cls.TRAINING_DATA_FILE)

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
            brain = Brain(name)

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

            brain.store_trained(x_train.columns.tolist(), score)

            return brain.info
        except FileNotFoundError as exc:
            raise BrainNoConfiguration(name) from exc
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(exc)
            raise LearningHouseException() from exc


class BrainPrediction():
    brains: Dict[str, Dict[str, int | Brain]] = {}

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

            if (brain.dataset.dependent_encode
                    and brain.estimatorcfg.typed == BrainEstimatorType.CLASSIFIER):
                prediction = brain.dataset.dependent_encoder.inverse_transform(
                    prediction)
                prediction = list(map(bool, prediction))
            else:
                prediction = list(map(float, prediction))

            return BrainPredictionResult(
                brain=brain.info,
                preprocessed=prepared_data.head(1).to_dict('records')[0],
                prediction=prediction[0]
            )
        except FileNotFoundError as exc:
            raise BrainNotTrained(name) from exc
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(exc)
            raise LearningHouseException() from exc

    @classmethod
    def _load_brain(cls, name: str) -> Brain:
        filename = sanitize_configuration_filename(
            name, Brain.TRAINED_FILE)
        stamp = stat(filename).st_mtime

        if not(name in cls.brains and cls.brains[name]['stamp'] == stamp):
            cls.brains[name] = {
                'stamp': stamp,
                'brain': Brain.load_trained(name)
            }

        return cls.brains[name]['brain']
