from os import environ
from pathlib import Path
from secrets import token_hex
from typing import Any, Dict, Optional, Union

import yaml
from pydantic import BaseModel, DirectoryPath

from learninghouse import versions
from learninghouse.core.logger.models import LoggingLevelEnum
from learninghouse.errors import LearningHouseException, LearningHouseValidationError

CONFIG_DIRECTORY_ENV = "LEARNINGHOUSE_CONFIG_DIRECTORY"

CONFIGURATION_FILENAME = "configuration.yaml"
SECRETS_FILENAME = "secrets.yaml"

# Fields that must never end up in configuration.yaml - readable only from
# secrets.yaml, the environment, or logged output. Shared with
# learninghouse.scripts.migrate_config so the settings loader and the
# migration script cannot drift apart on what counts as sensitive.
SECRET_FIELDS = {"jwt_secret"}

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

    config_directory: DirectoryPath = Path("./brains")

    logging_level: LoggingLevelEnum = LoggingLevelEnum.INFO

    jwt_secret: str = ""
    jwt_expire_minutes: int = 10

    def __init__(self, **data: Any):
        # Keys passed explicitly to the constructor take precedence over
        # every file-backed source below - otherwise an explicit
        # ServiceSettings(config_directory=...) is silently overwritten by
        # whatever configuration.yaml a stale directory happens to contain.
        explicit_keys = set(data.keys())

        config_directory = self._resolve_config_directory(data)

        if "config_directory" not in explicit_keys:
            data["config_directory"] = config_directory

        configuration = self._read_yaml_file(config_directory / CONFIGURATION_FILENAME)
        for key, value in configuration.items():
            # config_directory is the bootstrap value that determined where
            # this very file lives - it cannot also be set from inside it.
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
