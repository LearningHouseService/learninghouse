from __future__ import annotations

from datetime import datetime
from os import path, stat
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import joblib
import pandas as pd
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import accuracy_score

from learninghouse import versions
from learninghouse.api.errors.brain import (BrainNoConfiguration,
                                            BrainNotActual, BrainNotEnoughData,
                                            BrainNotTrained)
from learninghouse.core.logging import logger
from learninghouse.models import LearningHouseVersions
from learninghouse.models.brain import BrainInfo, BrainPredictionResult
from learninghouse.models.configuration import (
    BrainConfiguration,
    BrainEstimatorType, BrainFileType, sanitize_configuration_filename,
)
from learninghouse.models.preprocessing import DatasetConfiguration
from learninghouse.services.preprocessing import DatasetPreprocessing

if TYPE_CHECKING:
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


class Brain():
    def __init__(self, name: str):
        self.name: str = name
        self.configuration: BrainConfiguration = BrainConfiguration.from_json_file(
            name)

        self.dataset: DatasetConfiguration = DatasetConfiguration(
            self.configuration)

        self._estimator: Optional[RandomForestClassifier |
                                  RandomForestRegressor] = None

        self.score: Optional[float] = 0.0

        self.versions: LearningHouseVersions = versions

        self.trained_at: Optional[datetime] = None

    def estimator(self) -> RandomForestClassifier | RandomForestRegressor:
        if self._estimator is None:
            self._estimator = self.configuration.estimator.typed.estimator_class(
                n_estimators=self.configuration.estimator.estimators,
                max_depth=self.configuration.estimator.max_depth,
                random_state=self.configuration.estimator.random_state
            )

        return self._estimator

    @property
    def actual_versions(self) -> bool:
        return self.versions == versions

    @property
    def info(self) -> BrainInfo:
        info = BrainInfo(
            name=self.name,
            configuration=self.configuration,
            features=self.dataset.features,
            training_data_size=self.dataset.data_size,
            score=self.score,
            trained_at=self.trained_at,
            versions=self.versions,
            actual_versions=self.actual_versions
        )

        return info

    @classmethod
    def load_trained(cls, name: str) -> Brain:
        try:
            filename = sanitize_configuration_filename(
                name, BrainFileType.TRAINED_FILE)
            brain_config = joblib.load(filename)

            return brain_config
        except FileNotFoundError as exc:
            raise BrainNotTrained(name) from exc

    def store_trained(self,
                      columns: List[str],
                      training_data_size: int,
                      score: float) -> None:
        self.dataset.columns = columns
        self.dataset.data_size = training_data_size
        self.score = score
        self.trained_at = datetime.now()

        filename = sanitize_configuration_filename(
            self.name, BrainFileType.TRAINED_FILE)

        joblib.dump(self, filename)

        filename = sanitize_configuration_filename(
            self.name, BrainFileType.INFO_FILE)
        with open(filename, 'w', encoding='utf-8') as infofile:
            infofile.write(self.info.json(indent=4))


class BrainService():

    brains: Dict[str, Dict[str, int | Brain]] = {}

    @classmethod
    def request(cls, name: str, request_data: Optional[Dict[str, Any]] = None) -> BrainInfo:
        filename = sanitize_configuration_filename(
            name, BrainFileType.TRAINING_DATA_FILE)

        if request_data is None:
            if path.exists(filename):
                data = pd.read_csv(filename)
            else:
                raise BrainNotEnoughData()
        else:
            logger.debug(request_data)
            request_data = DatasetPreprocessing.add_time_information(
                request_data)
            if path.exists(filename):
                data_temp = pd.read_csv(filename)
                df_new_row = pd.DataFrame([request_data])
                data = pd.concat([data_temp, df_new_row], ignore_index=True)
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

            if BrainEstimatorType.CLASSIFIER == brain.configuration.estimator.typed:
                y_pred = estimator.predict(x_test)
                score = accuracy_score(y_test, y_pred)
            else:
                score = estimator.score(x_test, y_test)

            brain.store_trained(x_train.columns.tolist(),
                                len(data.index), score)

            return brain.info
        except FileNotFoundError as exc:
            raise BrainNoConfiguration(name) from exc

    @classmethod
    def prediction(cls, name: str, request_data: Dict[str, Any]):
        try:
            brain = cls.load_brain(name)
            if not brain.actual_versions:
                raise BrainNotActual(name, brain.versions)

            request_data = DatasetPreprocessing.add_time_information(
                request_data)

            data = pd.DataFrame([request_data])
            prepared_data = DatasetPreprocessing.prepare_prediction(
                brain, data)

            prediction = brain.estimator().predict(prepared_data)

            if (brain.configuration.dependent_encode
                    and brain.configuration.estimator.typed == BrainEstimatorType.CLASSIFIER):
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

    @classmethod
    def load_brain(cls, name: str) -> Brain:
        filename = sanitize_configuration_filename(
            name, BrainFileType.TRAINED_FILE)
        stamp = stat(filename).st_mtime

        if not (name in cls.brains and cls.brains[name]['stamp'] == stamp):
            cls.brains[name] = {
                'stamp': stamp,
                'brain': Brain.load_trained(name)
            }

        return cls.brains[name]['brain']
