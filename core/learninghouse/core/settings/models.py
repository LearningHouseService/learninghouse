from os import environ, listdir, path
from pathlib import Path
from secrets import token_hex
from typing import Any, Dict, Generator, Optional, Union

from pydantic import BaseModel, DirectoryPath

from learninghouse import versions
from learninghouse.api.errors import (
    LearningHouseException,
    LearningHouseValidationError,
)
from learninghouse.core.logging import LoggingLevelEnum

DOCKER_SECRETS_DIR = "/run/secrets"

LICENSE_URL = "https://github.com/LearningHouseService/learninghouse/blob/main/LICENSE"


class ServiceSettings(BaseModel):
    debug: Optional[bool] = False
    docs_url: str = "/docs"
    openapi_file: str = "/learninghouse_api.json"
    title: str = "learningHouse Service"

    host: str = "127.0.0.1"
    port: int = 5000

    workers: int = 1

    reload: bool = False
    base_url: str = ""

    environment: str = "production"

    config_directory: DirectoryPath = "./brains"

    logging_level: LoggingLevelEnum = LoggingLevelEnum.INFO

    jwt_secret: str = token_hex(16)
    jwt_expire_minutes: int = 10

    def __init__(self, **data: dict[str, any]):
        sources = [self._read_environment, self._read_dotenv, self._read_secrets]
        data = self._parse_key_and_values(sources, data)
        data = self.set_development_defaults(data)

        super().__init__(**data)

    def set_development_defaults(self, data: dict[str, any]) -> dict[str, any]:
        if "environment" in data and data["environment"] == "development":
            data = {
                **{
                    "debug": True,
                    "reload": True,
                    "title": "learningHouse Service - Development",
                },
                **data,
            }

        return data

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        validation_error = LearningHouseValidationError
        return {
            "debug": self.debug,
            "title": self.title,
            "openapi_url": self.openapi_file,
            "docs_url": None,
            "redoc_url": None,
            "version": versions.service,
            "responses": {
                validation_error.STATUS_CODE: validation_error.api_description(),
                LearningHouseException.STATUS_CODE: LearningHouseException.api_description(),
            },
            "license_info": {"name": "MIT License", "url": LICENSE_URL},
        }

    @property
    def uvicorn_kwargs(self) -> Dict[str, Any]:
        kwargs = {
            "host": self.host,
            "port": self.port,
            "headers": [("server", f"LearningHouse Service {versions.service}")],
        }

        if self.reload:
            kwargs["reload"] = True
        else:
            kwargs["workers"] = self.workers

        return kwargs

    @property
    def brains_directory(self) -> Path:
        return Path(self.config_directory).absolute()

    @property
    def base_url_calculated(self) -> str:
        if self.base_url:
            base_url = self.base_url
        elif self.host in ("0.0.0.0", "127.0.0.1"):
            base_url = "http://localhost"
        else:
            base_url = f"http://{self.host}"

        return f"{base_url}:{self.port}"

    @property
    def documentation_url(self) -> Union[str, None]:
        documentation_url = None

        if self.docs_url is not None:
            documentation_url = self.base_url_calculated + self.docs_url

        return documentation_url

    @property
    def openapi_url(self) -> str:
        return self.base_url_calculated + self.openapi_file

    @property
    def jwt_payload_claims(self) -> Dict[str, str]:
        return {"audience": "LearningHouseAPI", "issuer": "LearningHouse Service"}

    def _parse_key_and_values(
        self, sources: list[callable], data: dict[str, any]
    ) -> dict[str, any]:
        for source in sources:
            for key, value in source():
                key = key.lower().strip()[len("learninghouse_") :]  # remove prefix
                subkeys = key.split("__")  # get nested structure
                context = data
                for subkey in subkeys[:-1]:
                    if subkey not in context:
                        context[subkey] = {}
                    context = context[subkey]

                context[subkeys[-1]] = (
                    value.strip()
                )  # Missing possibility to set nested json values

        return data

    @classmethod
    def _read_environment(cls) -> Generator[tuple[str, str], any, any]:
        for key, value in environ.items():
            if cls._has_prefix(key):
                yield key, value

    @classmethod
    def _read_secrets(cls) -> Generator[tuple[str, str], any, any]:
        if path.exists(DOCKER_SECRETS_DIR) and path.isdir(DOCKER_SECRETS_DIR):
            for filename in listdir(DOCKER_SECRETS_DIR):
                if cls._has_prefix(filename):
                    with open(
                        path.join(DOCKER_SECRETS_DIR, filename), "r", encoding="utf-8"
                    ) as f:
                        yield filename, f.read()

    @classmethod
    def _read_dotenv(cls) -> Generator[tuple[str, str], any, any]:
        if path.exists(".env"):
            with open(".env", "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if cls._has_prefix(line) and "=" in line:
                        key, value = line.split("=", 1)
                        yield key, value

    @staticmethod
    def _has_prefix(key: str) -> bool:
        return key.lower().startswith("learninghouse_")
