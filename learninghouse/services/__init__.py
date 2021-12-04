from os import path

from learninghouse.api.errors import LearningHouseSecurityException
from learninghouse.core.settings import service_settings


def sanitize_configuration_filename(subdir: str, name: str, extension: str) -> str:
    filename = f'{name}.{extension}'
    base_path = str(service_settings().brains_directory / subdir)

    fullpath = path.normpath(path.join(base_path, filename))

    if not fullpath.startswith(base_path):
        raise LearningHouseSecurityException(
            'Configuration file name breaks configuration directory')

    return fullpath
