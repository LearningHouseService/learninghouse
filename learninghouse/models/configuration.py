from __future__ import annotations

import json
from os import makedirs, path
from typing import Dict, List, Optional, Type

from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from learninghouse.api.errors import LearningHouseSecurityException
from learninghouse.core.logging import logger
from learninghouse.core.settings import service_settings
from learninghouse.models.base import DictModel, EnumModel


class BrainEstimatorType(str, EnumModel):
    """
        **LearningHouse Service** can predict values using an estimator. An estimator can be
        of type `classifier` which fits best for your needs if you have somekind of categorical
        output like in the darkness example true and false. If you want to predict a numerical
        value for example the setpoint of an heating equipment use the type `regressor` instead.
    """
    CLASSIFIER = 'classifier', RandomForestClassifier
    REGRESSOR = 'regressor', RandomForestRegressor

    def __init__(self,
                 typed: str,
                 estimator_class: Type[RandomForestClassifier] |
                 Type[RandomForestRegressor]):
        # pylint: disable=super-init-not-called
        self._typed: str = typed
        self._estimator_class: Type[RandomForestClassifier] |\
            Type[RandomForestRegressor] = estimator_class

    @property
    def typed(self) -> str:
        return self._typed

    @property
    def estimator_class(self) -> Type[RandomForestClassifier] |\
            Type[RandomForestRegressor]:
        return self._estimator_class


class BrainEstimatorConfiguration(BaseModel):
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


class BrainConfiguration(BaseModel):
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

    estimator: BrainEstimatorConfiguration
    dependent: str = Field(None, example='darkness')
    dependent_encode: Optional[bool] = Field(False)
    test_size: Optional[float] = Field(0.2, gt=0.0, examples=[0.2, 20])

    @classmethod
    def from_json_file(cls, name: str) -> BrainConfiguration:
        filename = sanitize_configuration_filename(
            name, BrainFileType.CONFIG_FILE)

        with open(filename, 'r', encoding='utf-8') as config_file:
            return BrainConfiguration(**json.load(config_file))

    @classmethod
    def json_config_file_exists(cls, name: str) -> bool:
        filename = sanitize_configuration_filename(
            name, BrainFileType.CONFIG_FILE)
        return path.exists(filename)

    def to_json_file(self, name: str) -> None:
        brainpath = sanitize_configuration_directory(name)
        makedirs(brainpath, exist_ok=True)

        filename = sanitize_configuration_filename(
            name, BrainFileType.CONFIG_FILE)
        with open(filename, 'w', encoding='utf-8') as config_file:
            config_file.write(self.json(indent=4))


class BrainConfigurations(DictModel):
    __root__: Dict[str, BrainConfiguration]


class BrainConfigurationRequest(BaseModel):
    name: str = Field(None, example='darkness')
    configuration: BrainConfiguration


class BrainFileType(str, EnumModel):
    """
        Enumeration which holds the filetypes which are used for a brain
    """
    CONFIG_FILE = 'config', 'config.json'
    TRAINED_FILE = 'trained', 'trained.pkl'
    INFO_FILE = 'info', 'info.json'
    TRAINING_DATA_FILE = 'data', 'training_data.csv'
    ALL = 'all', ''

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

    def __eq__(self, other) -> bool:
        return EnumModel.equals(self, other)


class SensorDeleteResult(BaseModel):
    name: str = Field(None, example='azimuth')


class SensorType(str, EnumModel):
    NUMERICAL = 'numerical'
    CATEGORICAL = 'categorical'

    def __init__(self, typed: str):
        # pylint: disable=super-init-not-called
        self._typed: str = typed

    @property
    def typed(self) -> str:
        return self._typed

    def __eq__(self, other) -> bool:
        return EnumModel.equals(self, other)


class Sensor(BaseModel):
    name: str = Field(None, example='azimuth')
    typed: SensorType = Field(None, example=SensorType.NUMERICAL)


class Sensors(DictModel):
    __root__: Dict[str, SensorType] = Field(None, example={
        'azimuth': SensorType.NUMERICAL,
        'elevation': SensorType.NUMERICAL,
        'rain_gauge': SensorType.NUMERICAL,
        'pressure': SensorType.NUMERICAL,
        'pressure_trend_1h': SensorType.CATEGORICAL,
        'temperature_outside': SensorType.NUMERICAL,
        'temperature_trend_1h': SensorType.CATEGORICAL,
        'light_state': SensorType.CATEGORICAL
    })

    @classmethod
    def load_config(cls) -> Sensors:
        filename = service_settings().brains_directory / 'sensors.json'
        sensors = {}

        if path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as sensorfile:
                sensors = json.load(sensorfile)
        else:
            logger.warning('No sensors.json found')

        return Sensors.parse_obj(sensors)

    def write_config(self) -> None:
        filename = service_settings().brains_directory / 'sensors.json'
        with open(filename, 'w', encoding='utf-8') as sensorfile:
            json.dump(self.dict(), sensorfile, indent=4)

    @property
    def numericals(self) -> List[str]:
        return list(map(lambda x: x[0], filter(
            lambda x: x[1] == str(SensorType.NUMERICAL), self.items())))

    @ property
    def categoricals(self) -> List[str]:
        return list(map(lambda x: x[0], filter(
            lambda x: x[1] == str(SensorType.CATEGORICAL), self.items())))


class BrainDeleteResult(BaseModel):
    name: str = Field(None, example='darkness')


def sanitize_configuration_directory(brainname: str) -> str:
    brainpath = str(service_settings().brains_directory / brainname)

    fullpath = path.normpath(brainpath)

    if not fullpath.startswith(str(service_settings().brains_directory)):
        raise LearningHouseSecurityException(
            'Configuration file name breaks configuration directory')

    return fullpath


def sanitize_configuration_filename(brainname: str, filetype: BrainFileType) -> str:
    brainpath = sanitize_configuration_directory(brainname)

    fullpath = path.normpath(path.join(brainpath, filetype.filename))

    if not fullpath.startswith(str(service_settings().brains_directory)):
        raise LearningHouseSecurityException(
            'Configuration file name breaks configuration directory')

    return fullpath
