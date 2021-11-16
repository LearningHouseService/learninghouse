from typing import List

from learninghouse import ServiceVersions, versions
from learninghouse.estimator.api import EstimatorConfiguration
from pydantic import BaseModel


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
