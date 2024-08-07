from functools import lru_cache

from learninghouse.core.settings.models import ServiceSettings

@lru_cache()
def service_settings() -> ServiceSettings:
    return ServiceSettings()
