import time

from starlette.middleware.base import BaseHTTPMiddleware

from learninghouse.api.errors import LearningHouseException
from learninghouse.core.logging import logger


class CatchAllException(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(exc)
            return LearningHouseException().response()


class CustomHeader(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
