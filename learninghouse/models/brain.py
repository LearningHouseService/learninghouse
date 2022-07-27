from datetime import datetime
from typing import Dict, List, Union

from pydantic import BaseModel, Field

from learninghouse import versions
from learninghouse.models import LearningHouseVersions
from learninghouse.models.base import DictModel
from learninghouse.models.configuration import BrainConfiguration


class BrainInfo(BaseModel):
    """
    Information of the trained brain.
    """
    name: str = Field(None, example='darkness')
    configuration: BrainConfiguration = Field(None)
    features: List[str] = Field(
        None, example=['azimuth', 'elevation', 'rain_gauge', 'pressure_trend_1h_falling'])
    training_data_size: int = Field(None, example=1234)
    score: float = Field(None, example=0.85)
    trained_at: datetime = Field(
        None, example=datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'))
    versions: LearningHouseVersions = Field(None, example=versions)


class BrainTrainingRequest(DictModel):
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

    __root__: Dict[str, Union[int, float, str, bool, None]] = Field(None, example={
        'azimuth': 321.4441223144531,
        'elevation': -19.691608428955078,
        'rain_gauge': 0.0,
        'pressure': 971.0,
        'pressure_trend_1h': "falling",
        'temperature_outside': 23.0,
        'temperature_trend_1h': "rising",
        'light_state': False,
        'darkness': True
    })


class BrainPredictionRequest(DictModel):
    __root__: Dict[str, Union[int, float, str, bool, None]] = Field(None, example={
        'azimuth': 321.4441223144531,
        'elevation': -19.691608428955078,
        'rain_gauge': 0.0,
        'pressure': 971.0,
        'pressure_trend_1h': "falling",
        'temperature_outside': 23.0,
        'temperature_trend_1h': "rising",
        'light_state': False
    })


class BrainPredictionResult(BaseModel):
    brain: BrainInfo
    preprocessed: Dict[str, Union[int, float, str, bool]] = Field(None, example={
        'azimuth': 321.4441223144531,
        'elevation': -19.691608428955078,
        'rain_gauge': 0.0,
        'pressure_trend_1h_falling': 1
    })
    prediction: Union[bool, float] = Field(None, example=False)
