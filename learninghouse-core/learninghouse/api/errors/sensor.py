from typing import Dict

from fastapi import status

from learninghouse.api.errors import LearningHouseException
from learninghouse.models import LearningHouseErrorMessage

MIMETYPE_JSON = 'application/json'


class NoSensor(LearningHouseException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    NO_SENSOR = 'NO_SENSOR'
    DESCRIPTION = 'No sensor {name} found.'

    def __init__(self, name: str):
        super().__init__(self.STATUS_CODE,
                         self.NO_SENSOR,
                         self.DESCRIPTION.format(name=name))

    @classmethod
    def api_description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': 'No sensor with given name found',
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.NO_SENSOR,
                        'description': cls.DESCRIPTION
                    }
                }
            }
        }


class SensorExists(LearningHouseException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    EXISTS = 'EXISTS'
    DESCRIPTION = 'The existing sensor {name} can not be recreated. Use PUT to update.'

    def __init__(self, name: str):
        super().__init__(self.STATUS_CODE,
                         self.EXISTS,
                         self.DESCRIPTION.format(name=name))

    @classmethod
    def api_description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': 'An existing sensor can not be recreated. Use PUT to update.',
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.EXISTS,
                        'description': cls.DESCRIPTION
                    }
                }
            }
        }
