from __future__ import annotations

from os import listdir, path, stat
from shutil import rmtree
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

import pandas as pd
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import accuracy_score

from learninghouse.api.errors.brain import (
    BrainBadRequest,
    BrainExists,
    BrainNoConfiguration,
    BrainNotActual,
    BrainNotEnoughData,
    BrainNotTrained,
)
from learninghouse.core.logging import logger
from learninghouse.core.settings import service_settings
from learninghouse.models.brain import (
    Brain,
    BrainConfiguration,
    BrainDeleteResult,
    BrainEstimatorType,
    BrainFileType,
    BrainInfo,
    BrainInfos,
    BrainPredictionResult,
)
from learninghouse.services.preprocessing import DatasetPreprocessing

if TYPE_CHECKING:
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


class BrainService:
    brains: Dict[str, Dict[str, Union[int, Brain]]] = {}

    @classmethod
    def list_all(cls) -> BrainInfos:
        brains: Dict[str, BrainInfo] = {}
        for directory in listdir(service_settings().brains_directory):
            try:
                brains[directory] = cls.get_info(directory)
            except BrainNoConfiguration:
                pass

        return BrainInfos.parse_obj(brains)

    @staticmethod
    def get_info(name: str) -> BrainInfo:
        info: Optional[BrainInfo] = None
        if Brain.is_trained(name):
            try:
                info = Brain.load_trained(name).info
            except (AttributeError, BrainNotTrained):
                pass

        if info is None:
            if BrainConfiguration.json_config_file_exists(name):
                info = Brain(name).info
                training_data_file = Brain.sanitize_filename(
                    name, BrainFileType.TRAINING_DATA_FILE
                )
                if path.exists(training_data_file):
                    data = pd.read_csv(training_data_file)
                    info.training_data_size = len(data.index)
            else:
                raise BrainNoConfiguration(name)

        return info

    @classmethod
    def request(
        cls,
        name: str,
        dependent_value: Optional[Any] = None,
        sensors_data: Optional[Dict[str, Any]] = None
    ) -> BrainInfo:
        filename = Brain.sanitize_filename(
            name, BrainFileType.TRAINING_DATA_FILE)

        trainings_data: Optional[Dict[str, Any]] = sensors_data

        if sensors_data is not None:
            if dependent_value is not None:
                trainings_data[name] = dependent_value
            else:
                raise BrainBadRequest("Missing dependent variable!")

        if trainings_data is None:
            if path.exists(filename):
                data = pd.read_csv(filename)
            else:
                raise BrainNotEnoughData()
        else:
            logger.debug(trainings_data)
            trainings_data = DatasetPreprocessing.add_time_information(
                trainings_data)
            if path.exists(filename):
                data_temp = pd.read_csv(filename)
                df_new_row = pd.DataFrame([trainings_data])
                data = pd.concat([data_temp, df_new_row], ignore_index=True)
            else:
                data = pd.DataFrame([trainings_data])

            data.to_csv(filename, sep=",", index=False)

        return cls.train(name, data)

    @staticmethod
    def train(name: str, data: pd.DataFrame) -> BrainInfo:
        try:
            brain = Brain(name)

            if len(data.index) < 10:
                raise BrainNotEnoughData()

            (
                brain,
                x_train,
                x_test,
                y_train,
                y_test,
            ) = DatasetPreprocessing.prepare_training(brain, data, False)

            estimator = brain.estimator()

            selector = SelectFromModel(estimator)
            selector.fit(x_train, y_train)

            brain.dataset.features = x_train.columns[
                (selector.get_support())
            ].values.tolist()

            (
                brain,
                x_train,
                x_test,
                y_train,
                y_test,
            ) = DatasetPreprocessing.prepare_training(brain, data, True)

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
                raise BrainNotActual(name, brain.version)

            request_data = DatasetPreprocessing.add_time_information(
                request_data)

            data = pd.DataFrame([request_data])
            prepared_data = DatasetPreprocessing.prepare_prediction(
                brain, data)

            prediction = brain.estimator().predict(prepared_data)

            if (
                brain.configuration.dependent_encode
                and brain.configuration.estimator.typed == BrainEstimatorType.CLASSIFIER
            ):
                prediction = brain.dataset.dependent_encoder.inverse_transform(
                    prediction
                )
                prediction = list(map(bool, prediction))
            else:
                prediction = list(map(float, prediction))

            return BrainPredictionResult(
                brain=brain.info,
                preprocessed=prepared_data.head(1).to_dict("records")[0],
                prediction=prediction[0],
            )
        except FileNotFoundError as exc:
            raise BrainNotTrained(name) from exc

    @classmethod
    def load_brain(cls, name: str) -> Brain:
        filename = Brain.sanitize_filename(name, BrainFileType.TRAINED_FILE)
        stamp = stat(filename).st_mtime

        if not (name in cls.brains and cls.brains[name]["stamp"] == stamp):
            cls.brains[name] = {"stamp": stamp,
                                "brain": Brain.load_trained(name)}

        return cls.brains[name]["brain"]


class BrainConfigurationService:
    @staticmethod
    def get(name: str) -> BrainConfiguration:
        try:
            return BrainConfiguration.from_json_file(name)
        except FileNotFoundError as exc:
            raise BrainNoConfiguration(name) from exc

    @staticmethod
    def create(configuration: BrainConfiguration) -> BrainConfiguration:
        if BrainConfiguration.json_config_file_exists(configuration.name):
            raise BrainExists(configuration.name)

        configuration.to_json_file(configuration.name)

        return configuration

    @staticmethod
    def update(name: str, configuration: BrainConfiguration) -> BrainConfiguration:
        if not BrainConfiguration.json_config_file_exists(name):
            raise BrainNoConfiguration(name)

        configuration.to_json_file(name)

        return configuration

    @staticmethod
    def delete(name: str) -> BrainDeleteResult:
        brainpath = Brain.sanitize_directory(name)

        if not path.exists(brainpath):
            raise BrainNoConfiguration(name)

        logger.info(f"Remove brain: {name}")
        rmtree(brainpath)

        return BrainDeleteResult(name=name)
