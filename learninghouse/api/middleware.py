import time

from starlette.middleware.base import BaseHTTPMiddleware

from learninghouse.api.errors import LearningHouseException
from learninghouse.core.logging import logger

UNKNOWN_EXCEPTION_MESSAGE = """
An unknown error occured which is not handled by the service yet:
{exception}

Please open an issue at GitHub:
https://github.com/LearningHouseService/learninghouse-core/issues
"""


class CatchAllException(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error(UNKNOWN_EXCEPTION_MESSAGE.format(exception=exc))
            return LearningHouseException().response()


class CustomHeader(BaseHTTPMiddleware):
    # pylint: disable=too-few-public-methods
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
