from __future__ import annotations

import json
from datetime import datetime
from os import makedirs, path
from typing import Dict, List, Optional, Type

import joblib
from pydantic import Field, StrictBool, StrictFloat, StrictInt
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from learninghouse import versions
from learninghouse.api.errors import LearningHouseSecurityException
from learninghouse.api.errors.brain import BrainNotTrained
from learninghouse.core.settings import service_settings
from learninghouse.models import LearningHouseVersions
from learninghouse.models.base import DictModel, EnumModel, LHBaseModel
from learninghouse.models.preprocessing import DatasetConfiguration

settings = service_settings()


class BrainEstimatorType(EnumModel):
    """
    **LearningHouse Service** can predict values using an estimator. An estimator can be
    of type `classifier` which fits best for your needs if you have somekind of categorical
    output like in the darkness example true and false. If you want to predict a numerical
    value for example the setpoint of an heating equipment use the type `regressor` instead.
    """

    CLASSIFIER = "classifier", RandomForestClassifier
    REGRESSOR = "regressor", RandomForestRegressor

    def __init__(
        self,
        typed: str,
        estimator_class: Type[RandomForestClassifier] | Type[RandomForestRegressor]
    ):
        self._typed: str = typed
        self._estimator_class: Type[RandomForestClassifier] | Type[RandomForestRegressor] \
            = estimator_class

    @property
    def typed(self) -> str:
        return self._typed

    @property
    def estimator_class(
        self,
    ) -> Type[RandomForestClassifier] | Type[RandomForestRegressor]:
        return self._estimator_class


class BrainEstimatorConfiguration(LHBaseModel):
    """
    **LearningHouse Service** can predict values using an estimator.
    An estimator can be of type `classifier` which fits best for your
    needs if you have somekind of categorical output like in the
    darkness example true and false. If you want to predict a numerical
    value for example the setpoint of an heating equipment use the type
    `regressor` instead.

    For both types **learningHouse Service** uses a machine learning
    algorithm called random forest estimation. This algorithm builds
    a "forest" of decision trees with your `features` and takes the mean
    of the prediction of all of them to give you a best result. For more
    details see the API description of scikit-learn:

    | Estimator type | API Reference |
    |-----------------|-------------------|
    | RandomForestRegressor | \
        https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html#sklearn.ensemble.RandomForestRegressor |
    | RandomForestClassifier | \
        https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#sklearn.ensemble.RandomForestClassifier |

    You can adjust the amount of decision trees by using `estimators`
    (default: 100) option. And the maximum depth of each tree by using
    `max_depth` (default: 5) option. Both options are optional. Try to
    resize this value to optimize the accuracy of your model.
    """  # pylint: disable=line-too-long

    typed: BrainEstimatorType = Field(
        None, example=BrainEstimatorType.CLASSIFIER)
    estimators: Optional[int] = Field(100, ge=100, le=1000)
    max_depth: Optional[int] = Field(5, ge=4, le=10)
    random_state: Optional[int] = Field(0)


class BrainConfiguration(LHBaseModel):
    """
    Estimator:
    See BrainEstimatorConfiguration

    Dependent variable:
    The `dependent` variable is the one that have to be in the training data and which is predicted by the trained brain.

    The `dependent` variable has to be a number. If it is not a number, but a string or boolean (true/false) like in the example. For this set `dependent_encode` to true.

    Test size:
    LearningHouse service only uses a part of your training data to train the brain. The other part specified by `test_size` will be used to score the accuracy of your brain.

    Give a percentage by using floating point numbers between 0.01 and 0.99 or a absolute number of data points by using integer numbers.

    For the beginning a `test_size` of 20 % (0.2) like the example should be fine.
    """  # pylint: disable=line-too-long

    name: str = Field(None, example="darkness")
    estimator: BrainEstimatorConfiguration
    dependent_encode: Optional[bool] = Field(False)
    test_size: Optional[float] = Field(0.2, gt=0.0, examples=[0.2, 20])

    @classmethod
    def from_json_file(cls, name: str) -> BrainConfiguration:
        filename = Brain.sanitize_filename(name, BrainFileType.CONFIG_FILE)

        with open(filename, "r", encoding="utf-8") as config_file:
            return BrainConfiguration(**json.load(config_file))

    @classmethod
    def json_config_file_exists(cls, name: str) -> bool:
        filename = Brain.sanitize_filename(name, BrainFileType.CONFIG_FILE)
        return path.exists(filename)

    def to_json_file(self, name: str) -> None:
        brainpath = Brain.sanitize_directory(name)
        makedirs(brainpath, exist_ok=True)

        filename = Brain.sanitize_filename(name, BrainFileType.CONFIG_FILE)

        self.write_to_file(filename, indent=4)


class BrainConfigurations(DictModel):
    """
    A dictionary of all available brain configurations.
    """

    root: Dict[str, BrainConfiguration]


class BrainInfo(LHBaseModel):
    """
    Information of the brain about configuration, training data size, score,
    trained at and versions.
    """

    name: str = Field(None, example="darkness")
    configuration: BrainConfiguration = Field(None)
    features: Optional[List[str]] = Field(
        None,
        example=["azimuth", "elevation", "rain_gauge",
                 "pressure_trend_1h_falling"],
    )
    training_data_size: int = Field(None, example=1234)
    score: float = Field(None, example=0.85)
    trained_at: Optional[datetime] = Field(
        None, example=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    )
    versions: LearningHouseVersions = Field(None, example=versions)
    actual_versions: bool = Field(True)


class BrainInfos(DictModel):
    """A dictionary of all available brains."""

    root: Dict[str, BrainInfo]


class BrainFileType(EnumModel):
    """
    Enumeration which holds the filetypes which are used for a brain
    """

    CONFIG_FILE = "config", "config.json"
    TRAINED_FILE = "trained", "trained.pkl"
    INFO_FILE = "info", "info.json"
    TRAINING_DATA_FILE = "data", "training_data.csv"
    ALL = "all", ""

    def __init__(self, typed: str, filename: str):
        # pylint: disable=super-init-not-called
        self._typed: str = typed
        self._filename: str = filename

    @property
    def typed(self) -> str:
        return self._typed

    @property
    def filename(self) -> str:
        return self._filename


class Brain:
    def __init__(self, name: str):
        self.name: str = name
        self.configuration: BrainConfiguration = BrainConfiguration.from_json_file(
            name)

        self.dataset: DatasetConfiguration = DatasetConfiguration(
            self.configuration)

        self._estimator: Optional[
            RandomForestClassifier | RandomForestRegressor
        ] = None

        self.score: Optional[float] = 0.0

        self.versions: LearningHouseVersions = versions

        self.trained_at: Optional[datetime] = None

    def estimator(self) -> RandomForestClassifier | RandomForestRegressor:
        if self._estimator is None:
            self._estimator = self.configuration.estimator.typed.estimator_class(
                n_estimators=self.configuration.estimator.estimators,
                max_depth=self.configuration.estimator.max_depth,
                random_state=self.configuration.estimator.random_state,
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
            actual_versions=self.actual_versions,
        )

        return info

    @classmethod
    def load_trained(cls, name: str) -> Brain:
        try:
            if not cls.is_trained(name):
                raise BrainNotTrained(name)

            filename = Brain.sanitize_filename(
                name, BrainFileType.TRAINED_FILE)

            loaded_brain = joblib.load(filename)

            return loaded_brain
        except (AttributeError, ModuleNotFoundError, KeyError) as exception:
            raise BrainNotTrained(name) from exception

    @classmethod
    def is_trained(cls, name: str) -> bool:
        filename = Brain.sanitize_filename(name, BrainFileType.TRAINED_FILE)
        return path.exists(filename)

    def store_trained(
        self, columns: List[str], training_data_size: int, score: float
    ) -> None:
        self.dataset.columns = columns
        self.dataset.data_size = training_data_size
        self.score = score
        self.trained_at = datetime.now()

        filename = Brain.sanitize_filename(
            self.name, BrainFileType.TRAINED_FILE)

        joblib.dump(self, filename)

        filename = Brain.sanitize_filename(self.name, BrainFileType.INFO_FILE)

        self.info.write_to_file(filename, 4)

    @staticmethod
    def sanitize_directory(name: str) -> str:
        brainpath = str(settings.brains_directory / name)

        fullpath = path.normpath(brainpath)

        if not fullpath.startswith(str(settings.brains_directory)):
            raise LearningHouseSecurityException(
                "Configuration file name breaks configuration directory"
            )

        return fullpath

    @classmethod
    def sanitize_filename(cls, name: str, filetype: BrainFileType) -> str:
        brainpath = cls.sanitize_directory(name)

        return path.normpath(path.join(brainpath, filetype.filename))


class BrainTrainingRequest(LHBaseModel):
    """
    For training with data send a PUT request to the service.

    You can send either a field `timestamp` with your dataset containing
    a UNIX-Timestamp or the service will add this information with its
    current time. The service generate some further time relevant fields
    inside the training dataset you can although use as `features`.
    These are `month_of_year`, `day_of_month`, `day_of_week`, `hour_of_day`
    and `minute_of_hour`

    If one of your sensors is not working at the moment and for this not
    sending a value the service will add a value by using the following
    rules. For `categorical data` all categorical columns will be set to
    zero. For `numerical data` the mean of all known training set values
    for this `feature` will be assumed.
    """

    dependent_value: StrictBool | StrictInt | StrictFloat = Field(
        None, example=True)
    sensors_data: Dict[str, StrictBool | StrictInt | StrictFloat | str | None] = \
        Field(None,
              example={
                  "azimuth": 321.4441223144531,
                  "elevation": -19.691608428955078,
                  "rain_gauge": 0.0,
                  "pressure": 971.0,
                  "pressure_trend_1h": "falling",
                  "temperature_outside": 23.0,
                  "temperature_trend_1h": "rising",
                  "light_state": False
              },
              )


class BrainPredictionRequest(DictModel):
    """
    For prediction send a POST request to the service.
    """

    root: Dict[str, StrictBool | StrictInt | StrictFloat | str | None] = Field(
        None,
        example={
            "azimuth": 321.4441223144531,
            "elevation": -19.691608428955078,
            "rain_gauge": 0.0,
            "pressure": 971.0,
            "pressure_trend_1h": "falling",
            "temperature_outside": 23.0,
            "temperature_trend_1h": "rising",
            "light_state": False,
        },
    )


class BrainPredictionResult(LHBaseModel):
    """
    The result of a prediction request."""

    brain: BrainInfo
    preprocessed: Dict[str, StrictBool | StrictInt | StrictFloat | str] = Field(
        None,
        example={
            "azimuth": 321.4441223144531,
            "elevation": -19.691608428955078,
            "rain_gauge": 0.0,
            "pressure_trend_1h_falling": 1,
        },
    )
    prediction: StrictBool | StrictInt | StrictFloat = Field(
        None, example=False)


class BrainDeleteResult(LHBaseModel):
    """
    The result of a delete request."""

    name: str = Field(None, example="darkness")
