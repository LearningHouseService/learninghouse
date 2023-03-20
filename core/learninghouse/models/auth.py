from __future__ import annotations

from datetime import datetime
from os import path
from random import randint
from secrets import token_hex
from typing import Dict, List, Union

from passlib.hash import sha512_crypt
from pydantic import Field

from learninghouse.api.errors.auth import APIKeyExists, NoAPIKey
from learninghouse.core.settings import service_settings
from learninghouse.models.base import EnumModel, LHBaseModel

settings = service_settings()


class LoginRequest(LHBaseModel):
    password: str = Field(None, example='MY_PASSWORD')


class PasswordRequest(LHBaseModel):
    old_password: str = Field(None, example='MY_OLD_PASSWORD')
    new_password: str = Field(None, example='MY_NEW_PASSWORD')


class Token(LHBaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field('Bearer')


class TokenPayload(LHBaseModel):
    sub: str
    iss: str
    aud: str
    jti: str
    exp: datetime
    iat: datetime

    @classmethod
    def create(cls, subject: str, expire: datetime, issue_time: datetime) -> TokenPayload:
        payload_args = settings.jwt_payload_claims

        return cls(
            sub=subject,
            iss=payload_args['issuer'],
            aud=payload_args['audience'],
            jti=token_hex(16),
            exp=expire,
            iat=issue_time
        )


class APIKeyRole(EnumModel):
    USER = 'user'
    TRAINER = 'trainer'

    def __init__(self, role: str):
        # pylint: disable=super-init-not-called
        self._role: str = role

    @property
    def role(self) -> str:
        return self._role


class UserRole(EnumModel):
    USER = 'user'
    TRAINER = 'trainer'
    ADMIN = 'admin'

    def __init__(self, role: str):
        # pylint: disable=super-init-not-called
        self._role: str = role

    @property
    def role(self) -> str:
        return self._role


class APIKeyRequest(LHBaseModel):
    description: str = Field(
        None,
        min_length=3,
        max_length=15,
        regex=r'^[A-Za-z]\w{1,13}[A-Za-z0-9]$',
        example='app_as_user')
    role: APIKeyRole = Field(None, example=APIKeyRole.USER)


class APIKeyInfo(APIKeyRequest):
    @classmethod
    def from_api_key(cls, api_key: APIKey) -> APIKeyInfo:
        return cls(
            description=api_key.description,
            role=api_key.role)


class APIKey(APIKeyRequest):
    key: str

    @classmethod
    def from_api_key_request(cls, api_key_request: APIKeyRequest, key: str):
        return cls(
            description=api_key_request.description,
            role=api_key_request.role,
            key=key)


SECURITY_FILENAME = settings.brains_directory / 'security.json'


class SecurityDatabase(LHBaseModel):
    admin_password: str
    api_keys: Dict[str, APIKey] = {}
    salt: str = token_hex(8)
    rounds: int = randint(400000, 999999)
    initial_password: bool = True

    @classmethod
    def load_or_write_default(cls) -> SecurityDatabase:
        database = None
        if path.exists(SECURITY_FILENAME):
            database = cls.parse_file(SECURITY_FILENAME, encoding='utf-8')
        else:
            database = cls(admin_password=sha512_crypt.hash('learninghouse'))
            database.write()

        return database

    def write(self):
        self.write_to_file(SECURITY_FILENAME, 4)

    def authenticate_password(self, password: str) -> bool:
        return sha512_crypt.verify(password, self.admin_password)

    def update_password(self, new_password) -> None:
        self.admin_password = sha512_crypt.hash(new_password)
        self.initial_password = False

    def create_apikey(self, create: APIKeyRequest) -> APIKey:
        if self.find_apikey_by_description(create.description):
            raise APIKeyExists(create.description)

        key = token_hex(16)
        hashed_key = sha512_crypt.hash(key, salt=self.salt, rounds=self.rounds)
        new_api_key = APIKey.from_api_key_request(create, hashed_key)
        self.api_keys[hashed_key] = new_api_key

        return APIKey.from_api_key_request(create, key)

    def delete_apikey(self, description: str) -> str:
        api_key = self.find_apikey_by_description(description, True)
        if not api_key:
            raise NoAPIKey(description)

        del self.api_keys[api_key.key]

        return description

    def list_api_keys(self) -> List[APIKeyInfo]:
        return [APIKeyInfo.from_api_key(x) for x in self.api_keys.values()]

    def find_apikey_by_key(self, key: str) -> Union[APIKeyInfo, None]:
        api_key_info = None
        hashed_key = sha512_crypt.hash(key, salt=self.salt, rounds=self.rounds)

        if hashed_key in self.api_keys:
            api_key_info = APIKeyInfo.from_api_key(self.api_keys[hashed_key])

        return api_key_info

    def find_apikey_by_description(
            self, description: str,
            full_api_key: bool = False) -> [APIKeyInfo, APIKey, None]:
        api_key_info = None

        for api_key in self.api_keys.values():
            if api_key.description == description:
                api_key_info = api_key
                break

        if not full_api_key and api_key_info:
            api_key_info = APIKeyInfo.from_api_key(api_key_info)

        return api_key_info
