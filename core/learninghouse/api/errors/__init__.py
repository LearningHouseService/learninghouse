from typing import Any, Dict, List, Optional

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from learninghouse.core.logger import logger
from learninghouse.models import (
    LearningHouseErrorMessage,
    LearningHouseValidationErrorMessage,
)

MIMETYPE_JSON = "application/json"


class LearningHouseException(Exception):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    UNKNOWN = "UNKNOWN"
    DESCRIPTION = "An unknown exception occurred " + "while handling your request."

    def __init__(
        self,
        status_code: Optional[int] = None,
        key: Optional[str] = None,
        description: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__()
        self.http_status_code: int = status_code or self.STATUS_CODE
        self.error: LearningHouseErrorMessage = LearningHouseErrorMessage(
            error=key or self.UNKNOWN, description=description or self.DESCRIPTION
        )
        self.headers = headers if headers else {}

    def response(self) -> JSONResponse:
        return JSONResponse(
            content=self.error.dict(),
            status_code=self.http_status_code,
            headers=self.headers,
        )

    @classmethod
    def api_description(cls) -> Dict:
        return {
            "model": LearningHouseErrorMessage,
            "description": "An exception occured which is not handled by the service now. "
            + "Please write an issue on GitHub.",
            "content": {
                MIMETYPE_JSON: {
                    "example": {"error": cls.UNKNOWN, "description": cls.DESCRIPTION}
                }
            },
        }


class LearningHouseSecurityException(LearningHouseException):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    SECURITY_EXCEPTION = "SECURITY_EXCEPTION"
    DESCRIPTION = "A security violation occured while handling your request."

    def __init__(self, description: str, key: Optional[str] = None):
        key = key or self.SECURITY_EXCEPTION

        super().__init__(self.STATUS_CODE, key, description or self.DESCRIPTION)

    @classmethod
    def api_description(cls) -> Dict:
        return {
            "model": LearningHouseErrorMessage,
            "description": "The request didn't pass security checks.",
            "content": {
                MIMETYPE_JSON: {
                    "example": {
                        "error": cls.SECURITY_EXCEPTION,
                        "description": cls.DESCRIPTION,
                    }
                }
            },
        }


class LearningHouseUnauthorizedException(LearningHouseException):
    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    UNAUTHORIZED = "UNAUTHORIZED"
    DESCRIPTION = "Could not validate credentials"

    def __init__(self, description: Optional[str] = None):
        super().__init__(
            self.STATUS_CODE,
            self.UNAUTHORIZED,
            description or self.DESCRIPTION,
            {"WWW-Authenticate": "Bearer"},
        )

    @classmethod
    def api_description(cls) -> Dict:
        return {
            "model": LearningHouseErrorMessage,
            "description": "The request didn't pass security checks.",
            "content": {
                MIMETYPE_JSON: {
                    "example": {
                        "error": cls.UNAUTHORIZED,
                        "description": cls.DESCRIPTION,
                    }
                }
            },
        }


class LearningHouseValidationError(LearningHouseException):
    STATUS_CODE = status.HTTP_422_UNPROCESSABLE_ENTITY
    VALIDATION_ERROR = "VALIDATION_ERROR"
    DESCRIPTION = "A validation error occurred while handling your request."

    def __init__(self, error: Optional[RequestValidationError] = None):
        super().__init__(
            self.STATUS_CODE, self.VALIDATION_ERROR, str(error) or self.DESCRIPTION
        )
        self.validations: List[Dict[str, Any]] = error.errors()

    @classmethod
    def api_description(cls) -> Dict:
        return {
            "model": LearningHouseValidationErrorMessage,
            "description": "The request didn't pass input validation",
            "content": {
                MIMETYPE_JSON: {
                    "example": {
                        "error": cls.VALIDATION_ERROR,
                        "description": cls.DESCRIPTION,
                        "validations": [
                            {
                                "loc": ["body", "..."],
                                "msg": "example",
                                "type": "value...",
                                "ctx": {},
                            }
                        ],
                    }
                }
            },
        }

    def response(self) -> JSONResponse:
        validation_error = LearningHouseValidationErrorMessage.from_error_message(
            self.error, self.validations
        )
        return JSONResponse(
            content=validation_error.dict(), status_code=self.http_status_code
        )


async def validation_error_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    return LearningHouseValidationError(exc).response()


async def learninghouse_exception_handler(_: Request, exc: LearningHouseException):
    response = exc.response()

    if isinstance(
        exc, (LearningHouseSecurityException, LearningHouseUnauthorizedException)
    ):
        logger.warning(exc.error.description)

    return response
