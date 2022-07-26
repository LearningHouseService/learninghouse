from fastapi import Security
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader

from learninghouse.api.errors import LearningHouseSecurityException
from learninghouse.core.logging import logger
from learninghouse.core.settings import service_settings

settings = service_settings()

API_KEY_NAME = 'X-LEARNINGHOUSE-API-KEY'

api_key_query = APIKeyQuery(name='api_key', auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)


async def protect(
    query: str = Security(api_key_query),
    header: str = Security(api_key_header),
    cookie: str = Security(api_key_cookie)
):
    if settings.api_key_required:
        api_key = None

        if query:
            api_key = query
        elif header:
            api_key = header
        elif cookie:
            api_key = cookie

        if api_key != settings.api_key:
            logger.warning('Could not validate credentials')
            raise LearningHouseSecurityException(
                'Could not validate credentials')

    return 'okay'
