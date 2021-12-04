from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Type, Union

from pydantic import BaseSettings, DirectoryPath

from learninghouse import versions
from learninghouse.core import LearningHouseEnum
from learninghouse.core.logging import LoggingLevelEnum

BASE_DIR = Path(__file__).parent.parent.parent


class ServiceSettings(BaseSettings):
    debug: bool = False
    docs_url: str = '/docs'
    openapi_prefix: str = ''
    openapi_url: str = '/openapi.json'
    redoc_url: Optional[str] = None
    title: str = 'learningHouse Service'

    host: str = '0.0.0.0'
    port: int = 5000
    reload: bool = False

    environment: str = 'production'

    config_directory: DirectoryPath = BASE_DIR / 'brains'

    logging_level: LoggingLevelEnum = LoggingLevelEnum.INFO

    class Config:  # pylint: disable=too-few-public-methods
        validate_assignment = True
        prefix = 'learninghouse_'

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {'debug': self.debug,
                'docs_url': self.docs_url,
                'openapi_prefix': self.openapi_prefix,
                'openapi_url': self.openapi_url,
                'redoc_url': self.redoc_url,
                'title': self.title,
                'version': versions.service
                }

    @property
    def uvicorn_kwargs(self) -> Dict[str, Any]:
        kwargs = {
            'host': self.host,
            'port': self.port
        }

        if self.reload:
            kwargs['reload'] = True

        return kwargs

    @property
    def brains_directory(self) -> Path:
        return Path(self.config_directory).absolute()

    @property
    def base_url(self) -> str:
        if self.host == '0.0.0.0' or self.host == '127.0.0.1':
            base_url = f'http://localhost:{self.port}'
        else:
            base_url = f'http://{self.host}:{self.port}'

        return base_url

    @property
    def documentation_url(self) -> Union[str, None]:
        documentation_url = None

        if self.docs_url is not None:
            documentation_url = self.base_url + self.docs_url
        elif self.redoc_url is not None:
            documentation_url = self.base_url + self.redoc_url

        return documentation_url


class ProductionSettings(ServiceSettings):
    class Config(ServiceSettings.Config):  # pylint: disable=too-few-public-methods
        env_file = '.env'


class DevelopmentSettings(ServiceSettings):
    environment: str = 'development'
    debug: bool = True
    reload: bool = True
    title: str = 'learningHouse Service - Development'

    class Config(ServiceSettings.Config):  # pylint: disable=too-few-public-methods
        env_file = '.env'
        env_prefix = 'learninghouse_'


class ServiceEnvironment(LearningHouseEnum):
    PROD = 'production', ProductionSettings
    DEV = 'development', DevelopmentSettings

    def __init__(self,
                 description: str,
                 settings_class: Union[Type[ProductionSettings], Type[DevelopmentSettings]]):
        self.description: str = description
        self.settings_class: Union[Type[ProductionSettings],
                                   Type[DevelopmentSettings]] = settings_class


class ServiceBaseSettings(BaseSettings):
    environment: ServiceEnvironment = ServiceEnvironment.PROD

    class Config:  # pylint: disable=too-few-public-methods
        env_file = '.env'
        env_prefix = 'learninghouse_'


@lru_cache()
def service_settings() -> ServiceSettings:
    environment = ServiceBaseSettings().environment
    return environment.settings_class()  # pylint: disable=no-member
