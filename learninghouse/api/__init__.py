from fastapi import APIRouter, Depends

from learninghouse import versions
from learninghouse.api import brain, configuration
from learninghouse.api.errors import LearningHouseSecurityException
from learninghouse.models import LearningHouseVersions
from learninghouse.services.authorization import protect

api = APIRouter(
    prefix='/api',
    responses={
        LearningHouseSecurityException.STATUS_CODE:
        LearningHouseSecurityException.api_description()
    })
api.include_router(brain.router)
api.include_router(configuration.router)


@api.get('/versions',
         response_model=LearningHouseVersions,
         summary='Get versions',
         description='Get versions of the service and the used libraries',
         tags=['service'],
         responses={
             200: {
                 'description': 'Successfully retrieved versions'
             }
         })
def get_versions():
    return versions
