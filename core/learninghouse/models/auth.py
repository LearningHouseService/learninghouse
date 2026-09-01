from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from os import path
from pathlib import Path
from secrets import token_hex
from typing import Dict, List, Union

from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)
from pydantic import Field

from learninghouse.core.settings import service_settings
from learninghouse.errors.auth import APIKeyExists, NoAPIKey
from learninghouse.models.base import EnumModel, LHBaseModel

password_hasher = PasswordHasher()

INITIAL_ADMIN_PASSWORD = "learninghouse"

API_KEY_BYTES = 16

API_KEY_HASH_PREFIX = "sha256$"


class LoginRequest(LHBaseModel):
    password: str = Field(..., examples=["MY_PASSWORD"])


class PasswordRequest(LHBaseModel):
    old_password: str = Field(..., examples=["MY_OLD_PASSWORD"])
    new_password: str = Field(..., examples=["MY_NEW_PASSWORD"])


class Token(LHBaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="Bearer")


class TokenPayload(LHBaseModel):
    sub: str
    iss: str
    aud: str
    jti: str
    exp: datetime
    iat: datetime

    @classmethod
    def create(
        cls, subject: str, expire: datetime, issue_time: datetime
    ) -> TokenPayload:
        payload_args = service_settings().jwt_payload_claims

        return cls(
            sub=subject,
            iss=payload_args["issuer"],
            aud=payload_args["audience"],
            jti=token_hex(16),
            exp=expire,
            iat=issue_time,
        )

    def verify_subject(self, subject: str) -> bool:
        return self.sub == subject


class APIKeyRole(EnumModel):
    USER = "user"
    TRAINER = "trainer"

    def __init__(self, role: str):
        # pylint: disable=super-init-not-called
        self._role: str = role

    @property
    def role(self) -> str:
        return self._role


class UserRole(EnumModel):
    USER = "user"
    TRAINER = "trainer"
    ADMIN = "admin"

    def __init__(self, role: str):
        # pylint: disable=super-init-not-called
        self._role: str = role

    @property
    def role(self) -> str:
        return self._role


class APIKeyRequest(LHBaseModel):
    description: str = Field(
        ...,
        min_length=3,
        max_length=15,
        pattern=r"^[A-Za-z]\w{1,13}[A-Za-z0-9]$",
        examples=["app_as_user"],
    )
    role: APIKeyRole = Field(..., examples=[APIKeyRole.USER])


class APIKeyInfo(APIKeyRequest):
    @classmethod
    def from_api_key(cls, api_key: APIKey) -> APIKeyInfo:
        return cls(description=api_key.description, role=api_key.role)


class APIKey(APIKeyRequest):
    key: str

    @classmethod
    def from_api_key_request(cls, api_key_request: APIKeyRequest, key: str) -> APIKey:
        return cls(
            description=api_key_request.description, role=api_key_request.role, key=key
        )


def _security_filename() -> Path:
    return service_settings().brains_directory / "security.json"


class SecurityDatabase(LHBaseModel):
    admin_password: str
    api_keys: Dict[str, APIKey] = {}
    salt: str = Field(default_factory=lambda: token_hex(8))
    initial_password: bool = True

    @classmethod
    def load_or_write_default(cls) -> SecurityDatabase:
        filename = _security_filename()

        database = None
        if path.exists(filename):
            database = cls.parse_file(filename, encoding="utf-8")
        else:
            database = cls(admin_password=password_hasher.hash(INITIAL_ADMIN_PASSWORD))
            database.write()

        return database

    def write(self):
        self.write_to_file(_security_filename(), 4)

    def authenticate_password(self, password: str) -> bool:
        try:
            password_hasher.verify(self.admin_password, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

        if password_hasher.check_needs_rehash(self.admin_password):
            self._rehash_password(password)

        return True

    def _rehash_password(self, password: str) -> None:
        self.admin_password = password_hasher.hash(password)
        self.write()

    def update_password(self, new_password) -> None:
        self.admin_password = password_hasher.hash(new_password)
        self.initial_password = False

    def create_apikey(self, create: APIKeyRequest) -> APIKey:
        if self.find_apikey_by_description(create.description):
            raise APIKeyExists(create.description)

        key = token_hex(API_KEY_BYTES)
        hashed_key = self.hash_api_key(key)
        new_api_key = APIKey.from_api_key_request(create, hashed_key)
        self.api_keys[hashed_key] = new_api_key

        return APIKey.from_api_key_request(create, key)

    def delete_apikey(self, description: str) -> str:
        api_key = self.find_apikey_by_description(description, True)
        if not isinstance(api_key, APIKey):
            raise NoAPIKey(description)

        del self.api_keys[api_key.key]

        return description

    def list_api_keys(self) -> List[APIKeyInfo]:
        return [APIKeyInfo.from_api_key(x) for x in self.api_keys.values()]

    def hash_api_key(self, key: str) -> str:
        digest = sha256(f"{self.salt}{key}".encode("utf-8")).hexdigest()
        return f"{API_KEY_HASH_PREFIX}{digest}"

    def find_apikey_by_key(self, key: str) -> Union[APIKeyInfo, None]:
        hashed_key = self.hash_api_key(key)

        if hashed_key in self.api_keys:
            return APIKeyInfo.from_api_key(self.api_keys[hashed_key])

        return None

    def find_apikey_by_description(
        self, description: str, full_api_key: bool = False
    ) -> Union[APIKeyInfo, APIKey, None]:
        api_key_info = None

        for api_key in self.api_keys.values():
            if api_key.description == description:
                api_key_info = api_key
                break

        if not full_api_key and api_key_info:
            api_key_info = APIKeyInfo.from_api_key(api_key_info)

        return api_key_info
