from os import environ
from pathlib import Path
from secrets import token_hex
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, DirectoryPath, Field, field_validator

from learninghouse import versions
from learninghouse.core.logger import logger
from learninghouse.core.logger.models import LoggingLevelEnum
from learninghouse.errors import LearningHouseException, LearningHouseValidationError

CONFIG_DIRECTORY_ENV = "LEARNINGHOUSE_CONFIG_DIRECTORY"

CONFIGURATION_FILENAME = "configuration.yaml"
SECRETS_FILENAME = "secrets.yaml"

SECRET_FIELDS = {"jwt_secret"}

LICENSE_URL = "https://github.com/LearningHouseService/learninghouse/blob/main/LICENSE"

JWT_SECRET_GENERATED_WARNING = """
No jwt_secret was found in {secrets_file}. A new one has been generated and
written there with mode 0600. Every session issued before this start is
invalid. Keep that file with your backups - losing it logs everyone out.
"""

WORKERS_UNSUPPORTED = (
    "workers must be 1 for now: refresh tokens and the security database are "
    "held per process, so a session issued by one worker is rejected by all "
    "the others. Support for several workers comes back once both move into "
    "shared storage."
)

UI_DEVELOPMENT_ORIGIN = "http://localhost:4200"

WILDCARD_ORIGIN_REFUSED = (
    'cors_allowed_origins must not contain "*": the service answers '
    "credentialed cross-origin requests, and a wildcard combined with "
    "credentials makes every web page a user visits able to call this "
    "service with their session. List the origins that need access instead."
)


class ServiceSettings(BaseModel):
    debug: Optional[bool] = False
    docs_url: str = "/docs"
    openapi_file: str = "/learninghouse_api.json"
    title: str = "learningHouse Service"

    host: str = "127.0.0.1"
    port: int = 5000

    workers: int = 1

    cors_allowed_origins: List[str] = Field(default_factory=list)

    allow_api_key_query: bool = False

    reload: bool = False
    base_url: str = ""

    environment: str = "production"

    config_directory: DirectoryPath = Path("./brains")

    logging_level: LoggingLevelEnum = LoggingLevelEnum.INFO

    jwt_secret: str = ""
    jwt_expire_minutes: int = 10

    @field_validator("workers")
    @classmethod
    def validate_workers(cls, value: int) -> int:
        if value > 1:
            raise ValueError(WORKERS_UNSUPPORTED)

        return value

    @field_validator("cors_allowed_origins")
    @classmethod
    def validate_cors_allowed_origins(cls, value: List[str]) -> List[str]:
        origins = [origin.strip().rstrip("/") for origin in value]

        if "*" in origins:
            raise ValueError(WILDCARD_ORIGIN_REFUSED)

        return [origin for origin in origins if origin]

    def __init__(self, **data: Any):
        explicit_keys = set(data.keys())

        config_directory = self._resolve_config_directory(data)

        if "config_directory" not in explicit_keys:
            data["config_directory"] = config_directory

        configuration = self._read_yaml_file(config_directory / CONFIGURATION_FILENAME)
        for key, value in configuration.items():
            if (
                key in explicit_keys
                or key == "config_directory"
                or key in SECRET_FIELDS
            ):
                continue
            data[key] = value

        if "jwt_secret" not in explicit_keys:
            data["jwt_secret"] = self._resolve_jwt_secret(config_directory)

        data = self.set_development_defaults(data)

        super().__init__(**data)

    @staticmethod
    def _resolve_config_directory(data: Dict[str, Any]) -> Path:
        if "config_directory" in data:
            return Path(data["config_directory"])

        env_value = environ.get(CONFIG_DIRECTORY_ENV)
        if env_value:
            return Path(env_value)

        return Path("./brains")

    @classmethod
    def _resolve_jwt_secret(cls, config_directory: Path) -> str:
        secrets_file = config_directory / SECRETS_FILENAME
        secrets = cls._read_yaml_file(secrets_file)

        jwt_secret = secrets.get("jwt_secret")
        if not jwt_secret:
            jwt_secret = token_hex(16)
            secrets["jwt_secret"] = jwt_secret
            cls._write_secrets_file(secrets_file, secrets)
            logger.warning(
                JWT_SECRET_GENERATED_WARNING.format(secrets_file=secrets_file)
            )

        return jwt_secret

    @staticmethod
    def _read_yaml_file(file_path: Path) -> Dict[str, Any]:
        if not file_path.exists():
            return {}

        with open(file_path, "r", encoding="utf-8") as handle:
            content = yaml.safe_load(handle)

        return content or {}

    @staticmethod
    def _write_secrets_file(file_path: Path, secrets: Dict[str, Any]) -> None:
        with open(file_path, "w", encoding="utf-8") as handle:
            yaml.safe_dump(secrets, handle, sort_keys=False)

        file_path.chmod(0o600)

    def set_development_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if "environment" in data and data["environment"] == "development":
            data = {
                **{
                    "debug": True,
                    "reload": True,
                    "title": "learningHouse Service - Development",
                    "cors_allowed_origins": [UI_DEVELOPMENT_ORIGIN],
                },
                **data,
            }

        return data

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        validation_error = LearningHouseValidationError
        exception = LearningHouseException
        return {
            "debug": self.debug,
            "title": self.title,
            "openapi_url": self.openapi_file,
            "docs_url": None,
            "redoc_url": None,
            "version": versions.service,
            "responses": {
                validation_error.STATUS_CODE: validation_error.api_description(),
                exception.STATUS_CODE: exception.api_description(),
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
    def cors_origins(self) -> List[str]:
        origins = list(self.cors_allowed_origins)

        if self.base_url_calculated not in origins:
            origins.append(self.base_url_calculated)

        return origins

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
