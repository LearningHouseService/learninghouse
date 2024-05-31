from fastapi import APIRouter, Body, Depends, status

from learninghouse.api.errors.sensor import NoSensor, SensorExists
from learninghouse.models.sensor import Sensor, SensorDeleteResult, Sensors
from learninghouse.services.auth import authservice
from learninghouse.services.sensor import SensorConfigurationService

router = APIRouter(prefix="/sensor", tags=["sensor"])

router_usage = APIRouter(dependencies=[Depends(authservice.protect_user)])

router_admin = APIRouter(dependencies=[Depends(authservice.protect_admin)])


@router_usage.get(
    "s/configuration",
    response_model=Sensors,
    summary="Get all sensors configuration",
    description="Get all configured sensors.",
    responses={status.HTTP_200_OK: {"description": "All configured sensors"}},
)
async def get_sensors_configuration():
    return SensorConfigurationService.list_all()


@router_admin.get(
    "/{name}/configuration",
    response_model=Sensor,
    summary="Get sensor configuration",
    description="Get the current configuration of the given sensor",
    responses={
        status.HTTP_200_OK: {"description": "Configuration of the sensor"},
        NoSensor.STATUS_CODE: NoSensor.api_description(),
    },
)
async def get_sensor_configuration(name: str):
    return SensorConfigurationService.get(name)


@router_admin.post(
    "/configuration",
    response_model=Sensor,
    summary="Create a new sensor",
    description="Add a new sensor configuration.",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Added new sensor"},
        SensorExists.STATUS_CODE: SensorExists.api_description(),
    },
)
async def post_sensor_configuration(sensor: Sensor):
    return SensorConfigurationService.create(sensor.name, sensor.typed)


@router_admin.put(
    "/{name}/configuration",
    response_model=Sensor,
    summary="Update a sensor",
    description="Update a existing sensor configuration.",
    responses={
        status.HTTP_200_OK: {"description": "Updated sensor"},
        NoSensor.STATUS_CODE: NoSensor.api_description(),
    },
)
async def put_sensor_configuration(name: str, sensor: Sensor = Body()):
    return SensorConfigurationService.update(name, sensor.typed, sensor.cycles, sensor.calc_sun_position)


@router_admin.delete(
    "/{name}/configuration",
    response_model=SensorDeleteResult,
    summary="Delete a sensor",
    description="Delete the configuration of a sensor.",
    responses={status.HTTP_200_OK: {"description": "DeleteSensor"}},
)
async def delete_sensor_configuration(name: str):
    return SensorConfigurationService.delete(name)


router.include_router(router_usage)
router.include_router(router_admin)
