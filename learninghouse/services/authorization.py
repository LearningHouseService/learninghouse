from typing import Union

from fastapi import Security
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery

from learninghouse.api.errors import LearningHouseSecurityException
from learninghouse.core.settings import service_settings

settings = service_settings()

API_KEY_NAME = 'X-LEARNINGHOUSE-API-KEY'

api_key_query = APIKeyQuery(name='api_key', auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def protect_user(
    query: str = Security(api_key_query),
    header: str = Security(api_key_header)
) -> bool:
    if settings.api_key_required:
        api_key = None

        if query:
            api_key = query
        elif header:
            api_key = header

        if not valid_user_key(api_key):
            raise LearningHouseSecurityException(
                'Could not validate credentials')

    return True


def valid_user_key(api_key: Union[str, None]) -> bool:
    return api_key and (api_key == settings.api_key or valid_admin_key(api_key))


async def protect_admin(
    query: str = Security(api_key_query),
    header: str = Security(api_key_header)
) -> bool:
    api_key = None

    if query:
        api_key = query
    elif header:
        api_key = header

    if not valid_admin_key(api_key):
        raise LearningHouseSecurityException(
            'Could not validate credentials')

    return True


def valid_admin_key(api_key: Union[str, None]) -> bool:
    return (api_key and settings.api_key_admin and settings.api_key_admin == api_key)
