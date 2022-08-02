
from fastapi import APIRouter, Body, Path, status, Depends

from learninghouse.api.errors.brain import BrainExists, BrainNoConfiguration
from learninghouse.api.errors.sensor import NoSensor, SensorExists
from learninghouse.models.configuration import (BrainConfiguration,
                                                BrainConfigurationRequest,
                                                BrainConfigurations,
                                                BrainDeleteResult,
                                                BrainFileType, Sensor,
                                                SensorDeleteResult, Sensors,
                                                SensorType)
from learninghouse.services.configuration import (BrainConfigurationService,
                                                  SensorConfigurationService)
from learninghouse.services.auth import auth_service

brain_router = APIRouter(
    prefix='/brain',
    tags=['brain']
)


@brain_router.get('s/configuration',
                  response_model=BrainConfigurations,
                  summary='Get all brain configurations',
                  description='Get all configurations of trained brains.',
                  responses={
                      200: {
                          'description': 'All configured brains'
                      }
                  })
async def brains_get():
    return BrainConfigurationService.list_all()


@brain_router.get('/{name}/configuration',
                  response_model=BrainConfiguration,
                  summary='Get configuration of a brain',
                  description='Get the configuration of the specified brain',
                  responses={
                      status.HTTP_200_OK: {
                          'description': 'Configuration of the brain'
                      },
                      BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.api_description()
                  })
async def brain_get(name: str):
    return BrainConfigurationService.get(name)


@brain_router.post('/configuration',
                   response_model=BrainConfiguration,
                   summary='Create a new brain configuration',
                   description='Put the configuration of a new brain',
                   status_code=status.HTTP_201_CREATED,
                   responses={
                       status.HTTP_201_CREATED: {
                           'description': 'The new brain was created'
                       },
                       BrainExists.STATUS_CODE: BrainExists.api_description()
                   })
async def brain_post(brain: BrainConfigurationRequest):
    return BrainConfigurationService.create(brain.name, brain.configuration)


@brain_router.put('/{name}/configuration',
                  response_model=BrainConfiguration,
                  summary='Update brain configuration',
                  description='Post the configuration to update the brain',
                  responses={
                      status.HTTP_200_OK: {
                          'description': 'The brain configuration was updated'
                      },
                      BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.api_description()
                  })
async def brain_put(name: str, configuration: BrainConfiguration):
    return BrainConfigurationService.update(name, configuration)


@brain_router.delete('/{name}/configuration/{filetype}',
                     response_model=BrainDeleteResult,
                     summary='Delete specific file or whole brain',
                     responses={
                         status.HTTP_200_OK: {
                             'description': 'Returns the name of the brain and the deleted filetype'
                         }
                     })
async def brain_delete(name: str, filetype: BrainFileType = Path(BrainFileType.ALL)):
    return BrainConfigurationService.delete(name, filetype)

sensor_router = APIRouter(
    prefix='/sensor',
    tags=['sensor']
)


@sensor_router.get('s',
                   response_model=Sensors,
                   summary='Get all sensors',
                   description='Get all configured sensors.',
                   responses={
                       status.HTTP_200_OK: {
                           'description': 'All configured sensors'
                       }
                   })
async def sensors_get():
    return SensorConfigurationService.list_all()


@sensor_router.get('/{name}',
                   response_model=Sensor,
                   summary='Get sensor configuration',
                   description='Get the current configuration of the given sensor',
                   responses={
                       status.HTTP_200_OK: {
                           'description': 'Configuration of the sensor'
                       },
                       NoSensor.STATUS_CODE: NoSensor.api_description()
                   })
async def sensor_get(name: str):
    return SensorConfigurationService.get(name)


@sensor_router.post('/sensor',
                    response_model=Sensor,
                    summary='Create a new sensor',
                    description='Add a new sensor configuration.',
                    status_code=status.HTTP_201_CREATED,
                    responses={
                        status.HTTP_201_CREATED: {
                            'description': 'Added new sensor'
                        },
                        SensorExists.STATUS_CODE: SensorExists.api_description()
                    })
async def sensor_post(sensor: Sensor):
    return SensorConfigurationService.create(sensor.name, sensor.typed)


@sensor_router.put('/{name}',
                   response_model=Sensor,
                   summary='Update a sensor',
                   description='Update a existing sensor configuration.',
                   responses={
                       status.HTTP_200_OK: {
                           'description': 'Updated sensor'
                       },
                       NoSensor.STATUS_CODE: NoSensor.api_description()
                   })
async def sensor_put(name: str, typed: SensorType = Body()):
    return SensorConfigurationService.update(name, typed)


@sensor_router.delete('/{name}',
                      response_model=SensorDeleteResult,
                      summary='Delete a sensor',
                      description='Delete the configuration of a sensor.',
                      responses={
                          status.HTTP_200_OK: {
                              'description': 'DeleteSensor'
                          }
                      })
async def sensor_delete(name: str):
    return SensorConfigurationService.delete(name)

router = APIRouter(
    tags=['configuration'],
    dependencies=[Depends(auth_service().protect_admin)]
)

router.include_router(brain_router)
router.include_router(sensor_router)
