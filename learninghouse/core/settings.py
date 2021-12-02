from functools import lru_cache
from typing import Any, Dict, Optional, Union, Type
from pathlib import Path
from pydantic import BaseSettings, DirectoryPath

from learninghouse import versions
from learninghouse.core import LearningHouseEnum

BASE_DIR = Path(__file__).parent.parent.parent


class ServiceSettings(BaseSettings):
    debug: bool = False
    docs_url: str = '/docs'
    openapi_prefix: str = ''
    openapi_url: str = '/openapi.json'
    redoc_url: Optional[str] = None
    title: str = 'learningHouse Service'
    version: str = versions.service

    config_directory: DirectoryPath = BASE_DIR / 'brains'

    class Config:  # pylint: disable=too-few-public-methods
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            'debug': self.debug,
            'docs_url': self.docs_url,
            'openapi_prefix': self.openapi_prefix,
            'openapi_url': self.openapi_url,
            'redoc_url': self.redoc_url,
            'title': self.title,
            'version': self.version
        }

    @property
    def brains_directory(self) -> Path:
        return Path(self.config_directory).absolute()



class ProductionSettings(ServiceSettings):
    class Config(ServiceSettings.Config):  # pylint: disable=too-few-public-methods
        env_file = 'prod.env'


class DevelopmentSettings(ServiceSettings):
    debug: bool = True
    title: str = 'learningHouse Service - Development'

    class Config(ServiceSettings.Config):  # pylint: disable=too-few-public-methods
        env_file = '.env'


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


@lru_cache()
def service_settings() -> ServiceSettings:
    environment = ServiceBaseSettings().environment
    return environment.settings_class()  # pylint: disable=no-member
