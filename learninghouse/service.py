import uvicorn
from fastapi import FastAPI

from learninghouse import versions
from learninghouse.api import brain
from learninghouse.api.errors import LearningHouseException, learninghouse_exception_handler
from learninghouse.core.settings import service_settings
from learninghouse.core.logging import initialize_logging, logger

APP_REFERENCE = 'learninghouse.service:app'


def get_application() -> FastAPI:
    settings = service_settings()

    initialize_logging(settings.logging_level)

    application = FastAPI(**settings.fastapi_kwargs)
    application.include_router(brain.router)

    application.add_exception_handler(
        LearningHouseException, learninghouse_exception_handler)

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
