from typing import Optional

from fastapi import __version__ as fastapi_version
from numpy.version import version as np_version
from pandas import __version__ as pd_version
from pydantic import BaseModel
from pydantic.version import VERSION as pydantic_version
from sklearn import __version__ as skl_version
from uvicorn import __version__ as uvicorn_version
from jose import __version__ as jose_version
from passlib import __version__ as passlib_version
from loguru import __version__ as loguru_version

from learninghouse.models import LearningHouseVersions

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

versions = LearningHouseVersions(
    service=__version__,
    fastapi=fastapi_version,
    uvicorn=uvicorn_version,
    pydantic=pydantic_version,
    sklearn=skl_version,
    numpy=np_version,
    pandas=pd_version,
    jose=jose_version,
    passlib=passlib_version,
    loguru=loguru_version
)
