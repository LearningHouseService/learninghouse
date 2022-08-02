from datetime import datetime, timedelta
from functools import lru_cache
from typing import List

from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery
from jose import JWTError, jwt

from learninghouse.api.errors import (LearningHouseSecurityException,
                                      LearningHouseUnauthorizedException)
from learninghouse.core.logging import logger
from learninghouse.core.settings import service_settings
from learninghouse.models.auth import (APIKey, APIKeyInfo, APIKeyRequest,
                                       APIKeyRole, SecurityDatabase, Token,
                                       TokenPayload)

settings = service_settings()

API_KEY_NAME = 'X-LEARNINGHOUSE-API-KEY'

api_key_query = APIKeyQuery(name='api_key', auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
jwt_bearer = HTTPBearer(bearerFormat='JWT', auto_error=False)


class AuthService():
    JWT_SECRET_CONTENT = 'learninghouse_admin'

    def __init__(self):
        self.database = SecurityDatabase.load_or_write_default()

    @property
    def is_initial_admin_password(self) -> bool:
        return self.database.initial_password

    def login(self, password: str) -> Token:
        if not self.database.authenticate_password(password):
            raise LearningHouseSecurityException('Invalid password')

        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
        payload = TokenPayload(secret=self.JWT_SECRET_CONTENT, exp=expire)
        access_token = jwt.encode(payload.dict(), settings.jwt_secret, 'HS256')

        logger.info('Admin user logged in sucessfully')

        return Token(access_token=access_token)

    def update_password(self, old_password: str, new_password: str) -> bool:
        if not self.database.authenticate_password(old_password):
            raise LearningHouseSecurityException('Invalid old password')

        self.database.update_password(new_password)
        self.database.write()

        logger.info('New administration password set')

        return True

    def list_api_keys(self) -> List[APIKeyInfo]:
        return self.database.list_api_keys()

    def create_apikey(self, request: APIKeyRequest) -> APIKey:
        api_key = self.database.create_apikey(request)
        self.database.write()

        logger.info(f'New API key for {request.description} added')

        return api_key

    def delete_apikey(self, description: str) -> str:
        confirm = self.database.delete_apikey(description)
        self.database.write()

        logger.info(f'Removed API key for {description}.')

        return confirm

    @classmethod
    async def protect_admin(cls,
                            credentials: HTTPAuthorizationCredentials = Security(
                                jwt_bearer)
                            ) -> str:
        cls.validate_credentials(credentials, True)
        return 'admin'

    async def protect_user(self,
                           credentials: HTTPAuthorizationCredentials = Security(
                               jwt_bearer),
                           query: str = Security(api_key_query),
                           header: str = Security(api_key_header)) -> str:
        unlocked_by = self.is_admin_user_or_trainer(credentials, query, header)

        return unlocked_by

    async def protect_trainer(self,
                              credentials: HTTPAuthorizationCredentials = Security(
                                  jwt_bearer),
                              query: str = Security(api_key_query),
                              header: str = Security(api_key_header)) -> str:
        unlocked_by = self.is_admin_user_or_trainer(credentials, query, header)

        if unlocked_by not in ['jwt', APIKeyRole.TRAINER.role]:
            raise LearningHouseUnauthorizedException()

        return unlocked_by

    def is_admin_user_or_trainer(self,
                                 credentials: HTTPAuthorizationCredentials,
                                 query: str,
                                 header: str) -> str | None:
        unlocked_by = None

        if self.validate_credentials(credentials, False):
            unlocked_by = 'admin'
        else:
            key = query or header
            if not key:
                raise LearningHouseSecurityException('Invalid credentials')

            api_key_info = self.database.find_apikey_by_key(key)
            if not api_key_info:
                raise LearningHouseUnauthorizedException()

            unlocked_by = str(api_key_info.role)
        return unlocked_by

    @classmethod
    def validate_credentials(cls,
                             credentials: HTTPAuthorizationCredentials | None,
                             auto_error: bool) -> bool:
        is_valid = True

        if credentials:
            if credentials.scheme != 'Bearer':
                is_valid = False
                cls.raise_error_conditionally(
                    'Invalid authentication scheme.', auto_error)

            if not cls.verify_jwt(credentials.credentials):
                is_valid = False
                if auto_error:
                    raise LearningHouseUnauthorizedException()

        else:
            is_valid = False
            cls.raise_error_conditionally(
                'Invalid authorization code.', auto_error)

        return is_valid

    @staticmethod
    def raise_error_conditionally(description: str, auto_error: bool):
        if auto_error:
            raise LearningHouseSecurityException(description)

    @classmethod
    def verify_jwt(cls, access_token: str) -> bool:
        verified = False
        try:
            payload_data = jwt.decode(
                access_token, settings.jwt_secret, 'HS256')
            payload = TokenPayload.parse_obj(payload_data)
            verified = payload.secret == cls.JWT_SECRET_CONTENT
        except JWTError as exc:
            logger.error(exc)

        return verified


@lru_cache()
def auth_service() -> AuthService:
    service = AuthService()
    return service
