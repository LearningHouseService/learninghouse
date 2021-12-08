from typing import Dict, Optional

from fastapi import status, Request
from fastapi.responses import JSONResponse

from learninghouse.models import LearningHouseErrorMessage


class LearningHouseException(Exception):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    UNKNOWN = 'UNKNOWN'
    DESCRIPTION = 'An unknown exception occurred ' +\
        'while handling your request.'

    def __init__(self,
                 status_code: Optional[int] = None,
                 key: Optional[str] = None,
                 description: Optional[str] = None):
        super().__init__()
        self.http_status_code: int = status_code or self.STATUS_CODE
        self.error: LearningHouseErrorMessage = LearningHouseErrorMessage(
            error=key or self.UNKNOWN,
            description=description or self.DESCRIPTION
        )

    def response(self) -> JSONResponse:
        return JSONResponse(content=self.error.dict(), status_code=self.http_status_code)

    @classmethod
    def api_description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': 'An exception occured which is not handled by the service now. ' +
            'Please write an issue on GitHub.',
            'content': {
                'application/json': {
                    'example': {
                        'error': cls.UNKNOWN,
                        'description': cls.DESCRIPTION
                    }
                }
            }
        }


class LearningHouseSecurityException(LearningHouseException):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    SECURITY_EXCEPTION = 'SECURITY_EXCEPTION'
    DESCRIPTION = 'A security violation occured while handling your request.'

    def __init__(self, description: str):
        super().__init__(self.STATUS_CODE,
                         self.SECURITY_EXCEPTION,
                         description or self.DESCRIPTION)

    @classmethod
    def api_description(cls) -> Dict:
        return {
            'model': LearningHouseErrorMessage,
            'description': 'The request didn\'t pass security checks.',
            'content': {
                'application/json': {
                    'example': {
                        'error': cls.SECURITY_EXCEPTION,
                        'description': cls.DESCRIPTION
                    }
                }
            }
        }


async def learninghouse_exception_handler(request: Request, exc: LearningHouseException):  # pylint: disable=unused-argument
    return exc.response()
