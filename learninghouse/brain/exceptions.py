from typing import Dict, Optional

from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from learninghouse.brain.api import BrainErrorMessage

MIMETYPE_JSON = 'application/json'


class BrainException(Exception):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    UNKNOWN = 'UNKNOWN'

    def __init__(self,
                 status_code: Optional[int] = None,
                 key: Optional[str] = None,
                 description: Optional[str] = None):
        super().__init__()
        self.http_status_code: int = status_code or self.STATUS_CODE
        self.error: BrainErrorMessage = BrainErrorMessage(
            error=key or self.UNKNOWN,
            description=description or ''
        )

    def response(self) -> JSONResponse:
        return JSONResponse(content=self.error.dict(), status_code=self.http_status_code)

    @classmethod
    def description(cls) -> Dict:
        return {
            'model': BrainErrorMessage,
            'description': 'An exception occured which is not handled by the service now. Please write an issue on GitHub.',
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.UNKNOWN,
                        'description': ''
                    }
                }
            }
        }


class BrainNotTrained(BrainException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    NOT_TRAINED = 'NOT_TRAINED'

    def __init__(self):
        super().__init__(self.STATUS_CODE, self.NOT_TRAINED)

    @classmethod
    def description(cls) -> Dict:
        return {
            'model': BrainErrorMessage,
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


class BrainNotActual(BrainException):
    STATUS_CODE = status.HTTP_428_PRECONDITION_REQUIRED
    NOT_ACTUAL = 'NOT_ACTUAL'

    def __init__(self):
        super().__init__(self.STATUS_CODE, self.NOT_ACTUAL)

    @classmethod
    def description(cls) -> Dict:
        return {
            'model': BrainErrorMessage,
            'description': 'If brain was not compiled with actual versions of service and libraries.',
            'content': {
                MIMETYPE_JSON: {
                    'example': {
                        'error': cls.NOT_ACTUAL,
                        'description': ''
                    }
                }
            }
        }
