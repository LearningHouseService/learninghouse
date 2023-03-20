import logging
import sys
from pprint import pformat
from types import FrameType
from typing import cast

from loguru import logger
from loguru._defaults import LOGURU_FORMAT

from learninghouse.models.base import EnumModel


class LoggingLevelEnum(EnumModel):
    DEBUG = 'DEBUG', logging.DEBUG
    INFO = 'INFO', logging.INFO
    WARNING = 'WARNING', logging.WARNING
    ERROR = 'ERROR', logging.ERROR
    CRITICAL = 'CRITICAL', logging.CRITICAL

    def __init__(self,
                 description: str,
                 level: int):
        # pylint: disable=super-init-not-called
        self._description: str = description
        self._level: int = level

    @property
    def description(self) -> str:
        return self._description

    @property
    def level(self) -> int:
        return self._level


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


def format_record(record: dict) -> str:

    format_string = LOGURU_FORMAT
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string


def initialize_logging(logging_level: LoggingLevelEnum) -> None:
    logging_handler = LoggingHandler(level=logging_level.level)

    logging.basicConfig(handlers=[logging_handler], level=0)

    uvicorn_logger = logging.getLogger('uvicorn')
    uvicorn_logger.propagate = False

    for uvicorn_logger_name in ('fastapi', 'uvicorn.asgi', 'uvicorn.access'):
        logging.getLogger(uvicorn_logger_name).handlers = [logging_handler]

    logger.bind(request_id=None, method=None)

    logger.configure(
        handlers=[{"sink": sys.stdout,
                   "level": logging_level.level, "format": format_record}]
    )
