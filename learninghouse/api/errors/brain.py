from typing import Dict

from fastapi import status

from learninghouse import versions
from learninghouse.api.errors import LearningHouseException
from learninghouse.models import LearningHouseErrorMessage, LearningHouseVersions

MIMETYPE_JSON = 'application/json'


class BrainNotTrained(LearningHouseException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    NOT_TRAINED = 'NOT_TRAINED'
    DESCRIPTION = 'No trained brain with {name} found.'

    def __init__(self, name: str):
        super().__init__(self.STATUS_CODE,
                         self.NOT_TRAINED,
                         self.DESCRIPTION.format(name=name))

    @classmethod
    def api_description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': 'No trained brain with this name found.',
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.NOT_TRAINED,
                        'description': cls.DESCRIPTION
                    }
                }
            }
        }


class BrainNotActual(LearningHouseException):
    STATUS_CODE = status.HTTP_428_PRECONDITION_REQUIRED
    NOT_ACTUAL = 'NOT_ACTUAL'
    DESCRIPTION = 'The versions of trained brain {name} are ' + \
        'not the same as service. ' + \
        'Versions service: {versions}. ' + \
        'Versions brain: {brain_versions}. ' + \
        'Please train the brain again.'

    def __init__(self, name: str, brain_versions: LearningHouseVersions):
        super().__init__(self.STATUS_CODE,
                         self.NOT_ACTUAL,
                         self.DESCRIPTION.format(name=name,
                                                 versions=versions,
                                                 brain_versions=brain_versions))

    @classmethod
    def api_description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': 'If brain was not trained with actual versions ' +
            'of service and libraries.',
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.NOT_ACTUAL,
                        'description': cls.DESCRIPTION
                    }
                }
            }
        }


class BrainNotEnoughData(LearningHouseException):
    STATUS_CODE = status.HTTP_202_ACCEPTED
    NOT_ENOUGH_TRAINING_DATA = 'NOT_ENOUGH_TRAINING_DATA'
    DESCRIPTION = 'Brain was not trained because at least 10 data points are needed. ' + \
        'But your new data point was saved.'

    def __init__(self):
        super().__init__(self.STATUS_CODE,
                         self.NOT_ENOUGH_TRAINING_DATA,
                         self.DESCRIPTION)

    @classmethod
    def api_description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': 'Response if there are not enough data points.',
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.NOT_ENOUGH_TRAINING_DATA,
                        'description': cls.DESCRIPTION
                    }
                }
            }
        }


class BrainNoConfiguration(LearningHouseException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    NO_CONFIGURATION = 'NO_CONFIGURATION'
    DESCRIPTION = 'No configuration for brain {name} found.'

    def __init__(self, name: str):
        super().__init__(self.STATUS_CODE,
                         self.NO_CONFIGURATION,
                         self.DESCRIPTION.format(name=name))

    @classmethod
    def api_description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': 'No brain configuration found.',
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.NO_CONFIGURATION,
                        'description': cls.DESCRIPTION
                    }
                }
            }
        }


class BrainBadRequest(LearningHouseException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    BAD_REQUEST = 'BAD_REQUEST'

    def __init__(self, description: str):
        super().__init__(self.STATUS_CODE, self.BAD_REQUEST, description)

    @classmethod
    def api_description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': 'Brain received a bad request.',
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.BAD_REQUEST,
                        'description': ''
                    }
                }
            }
        }
