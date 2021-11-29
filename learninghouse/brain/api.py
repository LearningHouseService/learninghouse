from typing import Any, Dict, List

from pydantic import BaseModel

from learninghouse import ServiceVersions, versions
from learninghouse.estimator.api import EstimatorConfiguration


class BrainErrorMessage(BaseModel):
    error: str
    description: str = ''


class BrainInfo(BaseModel):
    name: str
    estimator_config: EstimatorConfiguration
    features: List[str]
    dependent: str
    dependent_encode: bool
    score: float
    versions: ServiceVersions

    class Config:
        # pylint: disable=too-few-public-methods
        schema_extra = {
            'example': {
                'name': 'darkness',
                'estimator_config': EstimatorConfiguration.Config.schema_extra['example'],
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
    class Config:
        # pylint: disable=too-few-public-methods
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
