from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version

from argon2 import __version__ as argon2_version
from fastapi import __version__ as fastapi_version
from jwt import __version__ as jwt_version
from loguru import (
    __version__ as loguru_version,  # pyright: ignore[reportAttributeAccessIssue]
)
from numpy.version import version as np_version
from pandas import __version__ as pd_version
from pydantic.version import VERSION as pydantic_version
from sklearn import __version__ as skl_version
from uvicorn import __version__ as uvicorn_version

from learninghouse.models import LearningHouseVersions

try:
    __version__ = package_version("learninghouse")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

versions = LearningHouseVersions(
    service=__version__,
    fastapi=fastapi_version,
    uvicorn=uvicorn_version,
    pydantic=pydantic_version,
    sklearn=skl_version,
    numpy=np_version,
    pandas=pd_version,
    jwt=jwt_version,
    argon2=argon2_version,
    loguru=loguru_version,
)
