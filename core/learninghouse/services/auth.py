from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Dict, List, Tuple, Union

import jwt
from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery

from learninghouse.core.logger import logger
from learninghouse.core.settings import service_settings
from learninghouse.core.settings.models import ServiceSettings
from learninghouse.errors import (
    LearningHouseSecurityException,
    LearningHouseUnauthorizedException,
)
from learninghouse.errors.auth import APIKeyInQueryStringNotAllowed, InvalidPassword
from learninghouse.models.auth import (
    APIKey,
    APIKeyInfo,
    APIKeyRequest,
    APIKeyRole,
    SecurityDatabase,
    Token,
    TokenPayload,
    UserRole,
)

API_KEY_NAME = "X-LEARNINGHOUSE-API-KEY"

API_KEY_QUERY_DEPRECATION = (
    "Deprecated. Query strings end up in access logs, proxy logs and browser "
    "history, so an API key sent this way has to be considered leaked. Send "
    "it in the {header} header instead. Only read at all while "
    "allow_api_key_query is set in configuration.yaml."
).format(header=API_KEY_NAME)

API_KEY_QUERY_WARNING = (
    "An API key was accepted from the query string. This is deprecated and "
    "the request's URL may have been written to access or proxy logs - treat "
    "the key as leaked and replace it once the client sends the "
    f"{API_KEY_NAME} header."
)

UNKNOWN_API_KEY_WARNING = (
    "Rejected an unknown API key presented in the {source}. Repeated "
    "occurrences mean somebody is trying keys against this service."
)

INVALID_PASSWORD_WARNING = (
    "Rejected an administration login with a wrong password. Repeated "
    "occurrences mean somebody is trying passwords against this service."
)

api_key_query = APIKeyQuery(
    name="api_key", auto_error=False, description=API_KEY_QUERY_DEPRECATION
)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
jwt_bearer = HTTPBearer(bearerFormat="JWT", auto_error=False)


INITIAL_PASSWORD_WARNING = """
In order to activate the service you have to replace the fallback password.

See https://github.com/LearningHouseService/learninghouse-monorepo/tree/main/learninghouse#fallback-password
"""


class AuthServiceInternal:
    def __init__(self):
        self.database = SecurityDatabase.load_or_write_default()
        self.refresh_tokens: Dict[str, datetime] = {}

    @property
    def is_initial_admin_password(self) -> bool:
        return self.database.initial_password

    def create_token(self, password: str) -> Token:
        if not self.database.authenticate_password(password):
            logger.warning(INVALID_PASSWORD_WARNING)
            raise InvalidPassword()

        self.cleanup_refresh_tokens()
        token = self.create_new_token()

        logger.info("Admin user logged in sucessfully")

        return token

    def refresh_token(self, refresh_token_jti: str) -> Token:
        self.cleanup_refresh_tokens()

        if refresh_token_jti in self.refresh_tokens:
            del self.refresh_tokens[refresh_token_jti]

        token = self.create_new_token()

        logger.info("Admin token refreshed")

        return token

    def revoke_refresh_token(self, refresh_token_jti: Union[str, None]) -> bool:
        self.cleanup_refresh_tokens()

        if refresh_token_jti:
            if refresh_token_jti in self.refresh_tokens:
                del self.refresh_tokens[refresh_token_jti]

            logger.info("Logout admininstrator refresh token")

        return True

    def revoke_all_refresh_tokens(self) -> bool:
        self.refresh_tokens.clear()

        logger.warning("Revoked all refresh tokens")

        return True

    def cleanup_refresh_tokens(self):
        del_tokens = []
        for jti, expire in self.refresh_tokens.items():
            if expire < datetime.now(timezone.utc):
                del_tokens.append(jti)

        for jti in del_tokens:
            del self.refresh_tokens[jti]

    def create_new_token(self) -> Token:
        settings = service_settings()

        issuetime = datetime.now(timezone.utc)
        access_expire = issuetime + timedelta(minutes=1)
        access_payload = TokenPayload.create("admin", access_expire, issuetime)
        access_token = jwt.encode(
            access_payload.model_dump(), settings.jwt_secret, algorithm="HS256"
        )

        refresh_expire = issuetime + timedelta(minutes=settings.jwt_expire_minutes)
        refresh_payload = TokenPayload.create("refresh", refresh_expire, issuetime)
        refresh_token = jwt.encode(
            refresh_payload.model_dump(), settings.jwt_secret, algorithm="HS256"
        )

        self.refresh_tokens[refresh_payload.jti] = refresh_expire

        return Token(access_token=access_token, refresh_token=refresh_token)

    def update_password(self, old_password: str, new_password: str) -> bool:
        if not self.database.authenticate_password(old_password):
            raise InvalidPassword()

        self.database.update_password(new_password)
        self.database.write()
        self.refresh_tokens.clear()

        logger.info("New administration password set")

        return True

    def list_api_keys(self) -> List[APIKeyInfo]:
        return self.database.list_api_keys()

    def create_apikey(self, request: APIKeyRequest) -> APIKey:
        api_key = self.database.create_apikey(request)
        self.database.write()

        logger.info(f"New API key for {request.description} added")

        return api_key

    def delete_apikey(self, description: str) -> str:
        confirm = self.database.delete_apikey(description)
        self.database.write()

        logger.info(f"Removed API key for {description}.")

        return confirm

    def is_admin_user_or_trainer(
        self,
        credentials: HTTPAuthorizationCredentials,
        query: str,
        header: str,
        allow_api_key_query: bool = False,
    ) -> UserRole:
        role: UserRole

        is_valid, _ = self.validate_credentials(credentials, False, "admin")

        if is_valid:
            role = UserRole.ADMIN
        else:
            key = header
            source = "header"
            if not key and query:
                if not allow_api_key_query:
                    raise APIKeyInQueryStringNotAllowed()

                logger.warning(API_KEY_QUERY_WARNING)
                key = query
                source = "query string"

            if not key:
                raise LearningHouseSecurityException("Invalid credentials")

            api_key_info = self.database.find_apikey_by_key(key)
            if not api_key_info:
                logger.warning(UNKNOWN_API_KEY_WARNING.format(source=source))
                raise LearningHouseUnauthorizedException()

            role = UserRole.from_string(str(api_key_info.role))
        return role

    def validate_credentials(
        self,
        credentials: Union[HTTPAuthorizationCredentials, None],
        auto_error: bool,
        subject: str,
    ) -> Tuple[bool, Union[str, None]]:
        is_valid = True
        jti = None

        if credentials:
            if credentials.scheme != "Bearer":
                is_valid = False
                self.raise_error_conditionally(
                    "Invalid authentication scheme.", auto_error
                )

            verified, jti = self.verify_jwt(credentials.credentials, subject)

            if not verified:
                is_valid = False
                if auto_error:
                    raise LearningHouseUnauthorizedException()

        else:
            is_valid = False
            self.raise_error_conditionally("Invalid authorization code.", auto_error)

        return is_valid, jti

    @staticmethod
    def raise_error_conditionally(description: str, auto_error: bool):
        if auto_error:
            raise LearningHouseSecurityException(description)

    def verify_jwt(
        self, access_token: str, subject: str
    ) -> Tuple[bool, Union[str, None]]:
        verified = False
        jti = None

        settings = service_settings()
        payload_args = settings.jwt_payload_claims

        try:
            payload = TokenPayload(
                **jwt.decode(
                    access_token,
                    settings.jwt_secret,
                    algorithms=["HS256"],
                    audience=payload_args["audience"],
                    issuer=payload_args["issuer"],
                )
            )

            if not payload.verify_subject(subject):
                raise jwt.InvalidTokenError("Invalid subject")

            if subject == "refresh":
                verified = payload.jti in self.refresh_tokens and self.refresh_tokens[
                    payload.jti
                ] > datetime.now(timezone.utc)

                if not verified:
                    logger.error("No valid refresh token")
            else:
                verified = True

            jti = payload.jti
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as err:
            logger.info(err)

        return verified, jti


@lru_cache()
def auth_service_cached() -> AuthServiceInternal:
    service = AuthServiceInternal()
    return service


async def protect_admin(
    credentials: HTTPAuthorizationCredentials = Security(jwt_bearer),
    auth_service: AuthServiceInternal = Depends(auth_service_cached),
) -> UserRole:
    auth_service.validate_credentials(credentials, True, "admin")
    return UserRole.ADMIN


async def protect_refresh(
    credentials: HTTPAuthorizationCredentials = Security(jwt_bearer),
    auth_service: AuthServiceInternal = Depends(auth_service_cached),
) -> str:
    _, jti = auth_service.validate_credentials(credentials, True, "refresh")

    if jti is None:  # pragma: no cover - validate_credentials raises before
        raise LearningHouseUnauthorizedException()

    return jti


async def get_refresh(
    credentials: HTTPAuthorizationCredentials = Security(jwt_bearer),
    auth_service: AuthServiceInternal = Depends(auth_service_cached),
) -> Union[str, None]:
    is_valid, jti = auth_service.validate_credentials(credentials, False, "refresh")

    return jti if is_valid else None


async def protect_user(
    credentials: HTTPAuthorizationCredentials = Security(jwt_bearer),
    query: str = Security(api_key_query),
    header: str = Security(api_key_header),
    auth_service: AuthServiceInternal = Depends(auth_service_cached),
    settings: ServiceSettings = Depends(service_settings),
) -> UserRole:
    return auth_service.is_admin_user_or_trainer(
        credentials, query, header, settings.allow_api_key_query
    )


async def protect_trainer(
    credentials: HTTPAuthorizationCredentials = Security(jwt_bearer),
    query: str = Security(api_key_query),
    header: str = Security(api_key_header),
    auth_service: AuthServiceInternal = Depends(auth_service_cached),
    settings: ServiceSettings = Depends(service_settings),
) -> UserRole:
    role = auth_service.is_admin_user_or_trainer(
        credentials, query, header, settings.allow_api_key_query
    )

    if role.role not in ["admin", APIKeyRole.TRAINER.role]:
        raise LearningHouseUnauthorizedException()

    return role
