from os import path

from learninghouse.api.errors import LearningHouseSecurityException
from learninghouse.core.settings import service_settings


def sanitize_configuration_filename(brainname: str, filename: str) -> str:
    brainpath = str(service_settings().brains_directory / brainname)

    fullpath = path.normpath(path.join(brainpath, filename))

    if not fullpath.startswith(str(service_settings().brains_directory)):
        raise LearningHouseSecurityException(
            'Configuration file name breaks configuration directory')

    return fullpath
