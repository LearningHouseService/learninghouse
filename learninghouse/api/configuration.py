
from fastapi import APIRouter, Body, Path, status

from learninghouse.api.errors import LearningHouseSecurityException
from learninghouse.api.errors.brain import BrainExists, BrainNoConfiguration
from learninghouse.api.errors.sensor import NoSensor, SensorExists
from learninghouse.models.configuration import (BrainConfiguration,
                                                BrainConfigurationRequest,
                                                BrainConfigurations,
                                                BrainDeleteResult,
                                                BrainFileType, Sensor, Sensors,
                                                SensorType, SensorDeleteResult)
from learninghouse.services.configuration import (BrainConfigurationService,
                                                  SensorConfigurationService)

router = APIRouter(
    tags=['configuration'],
    responses={
        LearningHouseSecurityException.STATUS_CODE:
        LearningHouseSecurityException.api_description()
    }
)


@router.get('/brains/configuration',
            response_model=BrainConfigurations,
            summary='Get all brain configurations',
            description='Get all configurations of trained brains.',
            tags=['brain', 'information'],
            responses={
                200: {
                    'description': 'All configured brains'
                }
            })
async def brains_get():
    return BrainConfigurationService.list_all()


@router.get('/brain/{name}/configuration',
            response_model=BrainConfiguration,
            summary='Get configuration of a brain',
            description='Get the configuration of the specified brain',
            tags=['brain', 'information'],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Configuration of the brain'
                },
                BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.api_description()
            })
async def brain_get(name: str):
    return BrainConfigurationService.get(name)


@router.post('/brain/configuration',
             response_model=BrainConfiguration,
             summary='Create a new brain configuration',
             description='Put the configuration of a new brain',
             tags=['brain'],
             status_code=status.HTTP_201_CREATED,
             responses={
                 status.HTTP_201_CREATED: {
                     'description': 'The new brain was created'
                 },
                 BrainExists.STATUS_CODE: BrainExists.api_description()
             })
async def brain_post(brain: BrainConfigurationRequest):
    return BrainConfigurationService.create(brain.name, brain.configuration)


@router.put('/brain/{name}/configuration',
            response_model=BrainConfiguration,
            summary='Update brain configuration',
            description='Post the configuration to update the brain',
            tags=['brain'],
            responses={
                status.HTTP_200_OK: {
                    'description': 'The brain configuration was updated'
                },
                BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.api_description()
            })
async def brain_put(name: str, configuration: BrainConfiguration):
    return BrainConfigurationService.update(name, configuration)


@router.delete('/brain/{name}/configuration/{filetype}',
               response_model=BrainDeleteResult,
               summary='Delete specific file or whole brain',
               tags=['brain'],
               responses={
                   status.HTTP_200_OK: {
                       'description': 'Returns the name of the brain and the deleted filetype'
                   }
               })
async def brain_delete(name: str, filetype: BrainFileType = Path(BrainFileType.ALL)):
    return BrainConfigurationService.delete(name, filetype)


@router.get('/sensors',
            response_model=Sensors,
            summary='Get all sensors',
            description='Get all configured sensors.',
            tags=['sensor', 'information'],
            responses={
                status.HTTP_200_OK: {
                    'description': 'All configured sensors'
                }
            })
async def sensors_get():
    return SensorConfigurationService.list_all()


@router.get('/sensor/{name}',
            response_model=Sensor,
            summary='Get sensor configuration',
            description='Get the current configuration of the given sensor',
            tags=['sensor', 'information'],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Configuration of the sensor'
                },
                NoSensor.STATUS_CODE: NoSensor.api_description()
            })
async def sensor_get(name: str):
    return SensorConfigurationService.get(name)


@router.post('/sensor',
             response_model=Sensor,
             summary='Create a new sensor',
             description='Add a new sensor configuration.',
             tags=['sensor'],
             status_code=status.HTTP_201_CREATED,
             responses={
                 status.HTTP_201_CREATED: {
                     'description': 'Added new sensor'
                 },
                 SensorExists.STATUS_CODE: SensorExists.api_description()
             })
async def sensor_post(sensor: Sensor):
    return SensorConfigurationService.create(sensor.name, sensor.typed)


@router.put('/sensor/{name}',
            response_model=Sensor,
            summary='Update a sensor',
            description='Update a existing sensor configuration.',
            tags=['sensor'],
            responses={
                status.HTTP_200_OK: {
                    'description': 'Updated sensor'
                },
                NoSensor.STATUS_CODE: NoSensor.api_description()
            })
async def sensor_put(name: str, typed: SensorType = Body()):
    return SensorConfigurationService.update(name, typed)


@router.delete('/sensor/{name}',
               response_model=SensorDeleteResult,
               summary='Delete a sensor',
               description='Delete the configuration of a sensor.',
               tags=['sensor'],
               responses={
                   status.HTTP_200_OK: {
                       'description': 'DeleteSensor'
                   }
               })
async def sensor_delete(name: str):
    return SensorConfigurationService.delete(name)
