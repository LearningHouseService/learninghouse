import time

from starlette.middleware.base import BaseHTTPMiddleware

from learninghouse.core.logger import logger
from learninghouse.core.settings.models import ServiceSettings
from learninghouse.errors import (
    LearningHouseException,
    LearningHouseUnauthorizedException,
)
from learninghouse.services.auth import INITIAL_PASSWORD_WARNING, AuthServiceInternal

UNKNOWN_EXCEPTION_MESSAGE = """
An unknown error occured which is not handled by the service yet:
{exception}

Please open an issue at GitHub:
https://github.com/LearningHouseService/learninghouse/issues
"""


class EnforceInitialPasswordChange(BaseHTTPMiddleware):
    # pylint: disable=too-few-public-methods
    ALLOWED_ENDPOINTS = [
        "/",
        "/api/auth/token",
        "/api/auth/password",
        "/api/mode",
        "/api/versions",
    ]

    def __init__(
        self,
        app,
        settings: ServiceSettings,
        auth_service: AuthServiceInternal,
        **kwargs,
    ):
        super().__init__(app, **kwargs)
        self.auth_service = auth_service
        self.endpoints = list(self.ALLOWED_ENDPOINTS)
        self.endpoints.append(settings.openapi_file)
        if settings.docs_url:
            self.endpoints.append(settings.docs_url)

    async def dispatch(self, request, call_next):
        endpoint = request.url.path
        if self.auth_service.is_initial_admin_password and not (
            endpoint in self.endpoints
            or endpoint.startswith("/static/")
            or endpoint.startswith("/ui")
        ):
            logger.warning(INITIAL_PASSWORD_WARNING)
            return LearningHouseUnauthorizedException(
                "Change initial password."
            ).response()

        return await call_next(request)


class CatchAllException(BaseHTTPMiddleware):
    # pylint: disable=too-few-public-methods
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error(UNKNOWN_EXCEPTION_MESSAGE.format(exception=exc))
            logger.exception(exc)
            return LearningHouseException().response()


class CustomHeader(BaseHTTPMiddleware):
    # pylint: disable=too-few-public-methods
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
