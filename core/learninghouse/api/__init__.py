from typing import Any, Dict, Union

from fastapi import APIRouter, Depends

from learninghouse import versions
from learninghouse.api import auth, brain, sensor
from learninghouse.core.settings import service_settings
from learninghouse.errors import LearningHouseSecurityException
from learninghouse.models import LearningHouseVersions
from learninghouse.services.auth import AuthServiceInternal, auth_service_cached

SECURITY_RESPONSE: Dict[Union[int, str], Dict[str, Any]] = {
    LearningHouseSecurityException.STATUS_CODE: (
        LearningHouseSecurityException.api_description()
    )
}

api = APIRouter(prefix="/api", responses=SECURITY_RESPONSE)

api.include_router(brain.router)
api.include_router(sensor.router)

api.include_router(auth.router)


@api.get("/mode", response_model=str, tags=["service"])
def get_mode(auth_service: AuthServiceInternal = Depends(auth_service_cached)):
    mode = service_settings().environment
    if auth_service.is_initial_admin_password:
        mode = "initial"

    return mode


@api.get(
    "/versions",
    response_model=LearningHouseVersions,
    summary="Get versions",
    description="Get versions of the service and the used libraries",
    tags=["service"],
    responses={200: {"description": "Successfully retrieved versions"}},
)
def get_versions():
    return versions
