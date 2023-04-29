from fastapi import APIRouter

from learninghouse import versions
from learninghouse.api import auth, brain, sensor
from learninghouse.api.errors import LearningHouseSecurityException
from learninghouse.core.settings import service_settings
from learninghouse.models import LearningHouseVersions
from learninghouse.services.auth import authservice

api = APIRouter(
    prefix="/api",
    responses={
        LearningHouseSecurityException.STATUS_CODE: LearningHouseSecurityException.api_description()
    },
)

api.include_router(brain.router)
api.include_router(sensor.router)

api.include_router(auth.router)


@api.get("/mode", response_model=str, tags=["service"])
def get_mode():
    mode = service_settings().environment
    if authservice.is_initial_admin_password:
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
