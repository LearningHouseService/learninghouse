import logging

from typing import Optional

from pydantic import BaseModel

from fastapi import __version__ as fastapi_version
from numpy.version import version as np_version
from pandas import __version__ as pd_version
from sklearn import __version__ as skl_version

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions


logging.basicConfig()
logger = logging.getLogger(__name__)

uvi_logger = logging.getLogger("uvicorn.error")
uvi_logger.propagate = False


class ServiceVersions(BaseModel):
    service: Optional[str] = __version__
    fastapi: Optional[str] = fastapi_version
    sklearn: Optional[str] = skl_version
    numpy: Optional[str] = np_version
    pandas: Optional[str] = pd_version


versions = ServiceVersions()
