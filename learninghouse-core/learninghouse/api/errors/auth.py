from typing import Dict

from fastapi import status

from learninghouse.api.errors import LearningHouseException, LearningHouseSecurityException
from learninghouse.models import LearningHouseErrorMessage

MIMETYPE_JSON = 'application/json'


class APIKeyExists(LearningHouseException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    EXISTS = 'APIKEY_EXISTS'
    DESCRIPTION = 'The existing api key {description} can not be recreated. Use DELETE recreate.'

    def __init__(self, description: str):
        super().__init__(self.STATUS_CODE,
                         self.EXISTS,
                         self.DESCRIPTION.format(description=description))

    @classmethod
    def api_description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': 'An existing api key can not be recreated. Use DELETE and recreate.',
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.EXISTS,
                        'description': cls.DESCRIPTION
                    }
                }
            }
        }


class NoAPIKey(LearningHouseException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    NO_APIKEY = 'NO_APIKEY'
    DESCRIPTION = 'No API key {description} found.'

    def __init__(self, description: str):
        super().__init__(self.STATUS_CODE,
                         self.NO_APIKEY,
                         self.DESCRIPTION.format(description=description))

    @classmethod
    def api_description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': 'No API key with given description found',
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.NO_APIKEY,
                        'description': cls.DESCRIPTION
                    }
                }
            }
        }


class InvalidPassword(LearningHouseSecurityException):
    INVALID_PASSWORD = 'INVALID_PASSWORD'
    DESCRIPTION = 'Invalid password'

    def __init__(self):
        super().__init__(self.DESCRIPTION, self.INVALID_PASSWORD)

    @classmethod
    def api_description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': cls.DESCRIPTION,
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.INVALID_PASSWORD,
                        'description': cls.DESCRIPTION
                    }
                }
            }
        }
