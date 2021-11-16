from typing import Optional

from pydantic import BaseModel


class EstimatorConfiguration(BaseModel):
    typed: str
    estimators: Optional[int] = 100
    max_depth: Optional[int] = 5
    random_state: Optional[int] = 0

    class Config:
        # pylint: disable=too-few-public-methods
        schema_extra = {
            'example': {
                'typed': 'classifier',
                'estimators': 100,
                'max_depth': 5,
                'random_state': 0
            }
        }
