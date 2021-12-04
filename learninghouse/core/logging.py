import logging
from types import FrameType
from typing import cast

from loguru import logger

from learninghouse.core import LearningHouseEnum


class LoggingLevelEnum(LearningHouseEnum):
    DEBUG = 'debug', logging.DEBUG
    INFO = 'info', logging.INFO
    WARNING = 'warning', logging.WARNING
    ERROR = 'error', logging.ERROR
    CRITICAL = 'critical', logging.CRITICAL

    def __init__(self, description: str, level: int):
        self.description: str = description
        self.level: int = level


class LoggingHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1

        log = logger.bind(request_id='app')
        log.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def initialize_logging(logging_level: LoggingLevelEnum) -> None:
    logging_handler = LoggingHandler(level=logging_level.level)

    logging.basicConfig(handlers=[logging_handler], level=0)

    uvicorn_logger = logging.getLogger('uvicorn')
    uvicorn_logger.propagate = False

    for uvicorn_logger_name in ('fastapi', 'uvicorn.asgi', 'uvicorn.access'):
        logging.getLogger(uvicorn_logger_name).handlers = [logging_handler]

    logger.bind(request_id=None, method=None)
