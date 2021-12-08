from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from learninghouse import versions
from learninghouse.api import brain, docs
from learninghouse.api.errors import (LearningHouseException,
                                      LearningHouseValidationError as ValidationError,
                                      learninghouse_exception_handler,
                                      validation_error_handler)
from learninghouse.core.logging import initialize_logging, logger
from learninghouse.core.settings import service_settings

APP_REFERENCE = 'learninghouse.service:app'

STATIC_DIRECTORY = str(Path(__file__).parent / 'static')


def get_application() -> FastAPI:
    settings = service_settings()

    initialize_logging(settings.logging_level)

    application = FastAPI(docs_url=None, redoc_url=None,
                          responses={
                              ValidationError.STATUS_CODE: ValidationError.api_description(),
                              LearningHouseException.STATUS_CODE: LearningHouseException.api_description()
                          },
                          **settings.fastapi_kwargs)
    application.include_router(brain.router)
    application.include_router(docs.router)

    application.add_exception_handler(
        RequestValidationError, validation_error_handler)
    application.add_exception_handler(
        LearningHouseException, learninghouse_exception_handler)

    application.mount(
        '/static', StaticFiles(directory=STATIC_DIRECTORY), name='static')

    return application


app = get_application()


def run():
    settings = service_settings()
    logger.info(f'Running {settings.title} {versions.service}')
    logger.info(versions.libraries_versions)
    logger.info(f'Running in {settings.environment} mode')
    logger.info(f'Listening on {settings.host}:{settings.port}')
    logger.info(f'Configuration directory {settings.brains_directory}')
    logger.info(f'URL to OpenAPI file {settings.openapi_url}')

    if settings.environment == 'production':
        if settings.debug:
            logger.warning(
                'Debugging active. Recommendation: Do not use in production mode!')

        if settings.reload:
            logger.warning(
                'Reloading active. Recommendation: Do not use in production mode!')

    if settings.documentation_url is not None:
        logger.info(
            f'See interactive documentation {settings.documentation_url}')

    uvicorn.run(app=APP_REFERENCE, log_config=None,
                **settings.uvicorn_kwargs)
