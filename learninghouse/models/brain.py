from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from learninghouse import versions
from learninghouse.core import LearningHouseEnum
from learninghouse.models import LearningHouseVersions


class BrainEstimatorType(LearningHouseEnum):
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
                 estimator_class: Union[Type[RandomForestClassifier],
                                        Type[RandomForestRegressor]]):
        self._typed: str = typed
        self._estimator_class: Union[Type[RandomForestClassifier],
                                     Type[RandomForestRegressor]] = estimator_class

    @property
    def typed(self) -> str:
        return self._typed

    @property
    def estimator_class(self) -> Union[Type[RandomForestClassifier],
                                       Type[RandomForestRegressor]]:
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
    typed: BrainEstimatorType
    estimators: Optional[int] = 100
    max_depth: Optional[int] = 5
    random_state: Optional[int] = 0

    class Config:  # pylint: disable=too-few-public-methods
        schema_extra = {
            'example': {
                'typed': 'classifier',
                'estimators': 100,
                'max_depth': 5,
                'random_state': 0
            }
        }


class BrainInfo(BaseModel):
    """
    Information of the trained brain.
    """
    name: str
    estimator_config: BrainEstimatorConfiguration
    features: List[str]
    dependent: str
    dependent_encode: bool
    score: float
    versions: LearningHouseVersions

    class Config:  # pylint: disable=too-few-public-methods
        schema_extra = {
            'example': {
                'name': 'darkness',
                'estimator_config': BrainEstimatorConfiguration.Config.schema_extra['example'],
                'features': ['azimuth', 'elevation', 'rain_gauge', 'pressure_trend_1h_falling'],
                'dependent': 'darkness',
                'dependent_encode': True,
                'score': 0.85,
                'versions': versions
            }
        }


class BrainRequest(BaseModel):
    data: Dict[str, Any]


class BrainTrainingRequest(BrainRequest):
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
    class Config:  # pylint: disable=too-few-public-methods
        schema_extra = {
            'example': {
                'data': {
                    'azimuth': 321.4441223144531,
                    'elevation': -19.691608428955078,
                    'rain_gauge': 0.0,
                    'pressure': 971.0,
                    'pressure_trend_1h': "falling",
                    'temperature_outside': 23.0,
                    'temperature_trend_1h': "rising",
                    'light_state': False,
                    'darkness': True
                }
            }
        }


class BrainPredictionRequest(BrainRequest):
    class Config:  # pylint: disable=too-few-public-methods
        schema_extra = {
            'example': {
                'data': {
                    'azimuth': 321.4441223144531,
                    'elevation': -19.691608428955078,
                    'rain_gauge': 0.0,
                    'pressure': 971.0,
                    'pressure_trend_1h': "falling",
                    'temperature_outside': 23.0,
                    'temperature_trend_1h': "rising",
                    'light_state': False
                }
            }
        }


class BrainPredictionResult(BaseModel):
    brain: BrainInfo
    preprocessed: Dict[str, Any]
    prediction: Union[bool, float]

    class Config:  # pylint: disable=too-few-public-methods
        schema_extra = {
            'example': {
                'brain': BrainInfo.Config.schema_extra['example'],
                'preprocessed': {
                    'azimuth': 321.4441223144531,
                    'elevation': -19.691608428955078,
                    'rain_gauge': 0.0,
                    'pressure_trend_1h_falling': 1
                },
                'prediction': True
            }
        }
