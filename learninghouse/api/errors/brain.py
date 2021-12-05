from typing import Dict

from fastapi import status

from learninghouse import versions
from learninghouse.api.errors import LearningHouseException
from learninghouse.models import LearningHouseErrorMessage, LearningHouseVersions

MIMETYPE_JSON = 'application/json'


class BrainNotTrained(LearningHouseException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    NOT_TRAINED = 'NOT_TRAINED'

    def __init__(self):
        super().__init__(self.STATUS_CODE, self.NOT_TRAINED)

    @classmethod
    def description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': 'No trained model with this name found.',
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.NOT_TRAINED,
                        'description': ''
                    }
                }
            }
        }


class BrainNotActual(LearningHouseException):
    STATUS_CODE = status.HTTP_428_PRECONDITION_REQUIRED
    NOT_ACTUAL = 'NOT_ACTUAL'

    def __init__(self, name: str, brain_versions: LearningHouseVersions):
        description = f'The versions of trained brain {name} are not the same as service. '
        description += f'Versions service: {versions}. '
        description += f'Versions brain: {brain_versions}. '
        description += 'Please train the brain again.'
        super().__init__(self.STATUS_CODE,
                         self.NOT_ACTUAL,
                         description)

    @classmethod
    def description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': 'If brain was not trained with actual versions of service and libraries.',
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.NOT_ACTUAL,
                        'description': ''
                    }
                }
            }
        }


class BrainNotEnoughData(LearningHouseException):
    STATUS_CODE = status.HTTP_202_ACCEPTED
    NOT_ENOUGH_TRAINING_DATA = 'NOT_ENOUGH_TRAINING_DATA'

    def __init__(self):
        super().__init__(self.STATUS_CODE, self.NOT_ENOUGH_TRAINING_DATA)

    @classmethod
    def description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': 'Brain needs at least 10 data points to be trained.',
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.NOT_ENOUGH_TRAINING_DATA,
                        'description': ''
                    }
                }
            }
        }


class BrainNoConfiguration(LearningHouseException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    NO_CONFIGURATION = 'NO_CONFIGURATION'

    def __init__(self):
        super().__init__(self.STATUS_CODE, self.NO_CONFIGURATION)

    @classmethod
    def description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': 'No brain configuration found.',
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.NO_CONFIGURATION,
                        'description': ''
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
    def description(cls) -> Dict:
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
