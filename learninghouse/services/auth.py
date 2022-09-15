from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Tuple

from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery
from jose import JWTError, jwt

from learninghouse.api.errors import (LearningHouseSecurityException,
                                      LearningHouseUnauthorizedException)
from learninghouse.api.errors.auth import InvalidPassword
from learninghouse.core.logging import logger
from learninghouse.core.settings import service_settings
from learninghouse.models.auth import (APIKey, APIKeyInfo, APIKeyRequest,
                                       APIKeyRole, SecurityDatabase, Token,
                                       TokenPayload, UserRole)

settings = service_settings()

API_KEY_NAME = 'X-LEARNINGHOUSE-API-KEY'

api_key_query = APIKeyQuery(name='api_key', auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
jwt_bearer = HTTPBearer(bearerFormat='JWT', auto_error=False)


INITIAL_PASSWORD_WARNING = """
In order to activate the service you have to replace the fallback password.

See https://github.com/LearningHouseService/learninghouse-core#security
"""


class AuthService():
    def __init__(self):
        self.database = SecurityDatabase.load_or_write_default()
        self.refresh_tokens: Dict[str, datetime] = {}

    @property
    def is_initial_admin_password(self) -> bool:
        return self.database.initial_password

    def create_token(self, password: str) -> Token:
        if not self.database.authenticate_password(password):
            raise InvalidPassword()

        self.cleanup_refresh_tokens()
        token = self.create_new_token()

        logger.info('Admin user logged in sucessfully')

        return token

    def refresh_token(self, refresh_token_jti: str) -> Token:
        self.cleanup_refresh_tokens()

        if refresh_token_jti in self.refresh_tokens:
            del self.refresh_tokens[refresh_token_jti]

        token = self.create_new_token()

        logger.info('Admin token refreshed')

        return token

    def revoke_refresh_token(self, refresh_token_jti: str | None) -> bool:

        self.cleanup_refresh_tokens()

        if refresh_token_jti:
            if refresh_token_jti in self.refresh_tokens:
                del self.refresh_tokens[refresh_token_jti]

            logger.info('Logout admininstrator refresh token')

        return True

    def revoke_all_refresh_tokens(self) -> bool:
        self.refresh_tokens.clear()

        logger.warning('Revoked all refresh tokens')

        return True

    def cleanup_refresh_tokens(self):
        del_tokens = []
        for jti, expire in self.refresh_tokens.items():
            if expire < datetime.utcnow():
                del_tokens.append(jti)

        for jti in del_tokens:
            del self.refresh_tokens[jti]

    def create_new_token(self) -> Token:
        issuetime = datetime.utcnow()
        access_expire = issuetime + timedelta(minutes=1)
        access_payload = TokenPayload.create('admin', access_expire, issuetime)
        access_token = jwt.encode(
            access_payload.dict(), settings.jwt_secret, 'HS256')

        refresh_expire = issuetime + \
            timedelta(minutes=settings.jwt_expire_minutes)
        refresh_payload = TokenPayload.create(
            'refresh', refresh_expire, issuetime)
        refresh_token = jwt.encode(
            refresh_payload.dict(), settings.jwt_secret, 'HS256')

        self.refresh_tokens[refresh_payload.jti] = refresh_expire

        return Token(access_token=access_token, refresh_token=refresh_token)

    def update_password(self, old_password: str, new_password: str) -> bool:
        if not self.database.authenticate_password(old_password):
            raise InvalidPassword()

        self.database.update_password(new_password)
        self.database.write()
        self.refresh_tokens.clear()

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

    async def protect_admin(self,
                            credentials: HTTPAuthorizationCredentials = Security(
                                jwt_bearer)
                            ) -> UserRole:
        self.validate_credentials(credentials, True, 'admin')
        return UserRole.ADMIN

    async def protect_refresh(self,
                              credentials: HTTPAuthorizationCredentials = Security(
                                  jwt_bearer)) -> str:
        _, jti = self.validate_credentials(credentials, True, 'refresh')

        return jti

    async def get_refresh(self,
                          credentials: HTTPAuthorizationCredentials = Security(
                              jwt_bearer)) -> str | None:
        is_valid, jti = self.validate_credentials(
            credentials, False, 'refresh')

        return jti if is_valid else None

    async def protect_user(self,
                           credentials: HTTPAuthorizationCredentials = Security(
                               jwt_bearer),
                           query: str = Security(api_key_query),
                           header: str = Security(api_key_header)) -> UserRole:
        role = self.is_admin_user_or_trainer(credentials, query, header)

        return role

    async def protect_trainer(self,
                              credentials: HTTPAuthorizationCredentials = Security(
                                  jwt_bearer),
                              query: str = Security(api_key_query),
                              header: str = Security(api_key_header)) -> UserRole:
        role = self.is_admin_user_or_trainer(credentials, query, header)

        if role.role not in ['admin', APIKeyRole.TRAINER.role]:
            raise LearningHouseUnauthorizedException()

        return role

    def is_admin_user_or_trainer(self,
                                 credentials: HTTPAuthorizationCredentials,
                                 query: str,
                                 header: str) -> UserRole | None:
        role = None

        is_valid, _ = self.validate_credentials(credentials, False, 'admin')

        if is_valid:
            role = UserRole.ADMIN
        else:
            key = query or header
            if not key:
                raise LearningHouseSecurityException('Invalid credentials')

            api_key_info = self.database.find_apikey_by_key(key)
            if not api_key_info:
                raise LearningHouseUnauthorizedException()

            role = UserRole.from_string(str(api_key_info.role))
        return role

    def validate_credentials(self,
                             credentials: HTTPAuthorizationCredentials | None,
                             auto_error: bool,
                             subject: str) -> Tuple[bool, str | None]:
        is_valid = True
        jti = None

        if credentials:
            if credentials.scheme != 'Bearer':
                is_valid = False
                self.raise_error_conditionally(
                    'Invalid authentication scheme.', auto_error)

            verified, jti = self.verify_jwt(credentials.credentials, subject)

            if not verified:
                is_valid = False
                if auto_error:
                    raise LearningHouseUnauthorizedException()

        else:
            is_valid = False
            self.raise_error_conditionally(
                'Invalid authorization code.', auto_error)

        return is_valid, jti

    @staticmethod
    def raise_error_conditionally(description: str, auto_error: bool):
        if auto_error:
            raise LearningHouseSecurityException(description)

    def verify_jwt(self, access_token: str, subject: str) -> Tuple[bool, str | None]:
        verified = False
        jti = None
        try:
            payload = TokenPayload.parse_obj(jwt.decode(
                access_token,
                settings.jwt_secret,
                'HS256',
                subject=subject,
                **settings.jwt_payload_claims))

            if subject == 'refresh':
                verified = (payload.jti in self.refresh_tokens
                            and self.refresh_tokens[payload.jti] > datetime.utcnow())

                if not verified:
                    logger.error('No valid refresh token')
            else:
                verified = True

            jti = payload.jti
        except JWTError as exc:
            logger.info(exc)

        return verified, jti


@lru_cache()
def auth_service() -> AuthService:
    service = AuthService()
    return service
