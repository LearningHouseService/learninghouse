from fastapi import APIRouter

from learninghouse.api.errors import LearningHouseException
from learninghouse.api.errors import \
    LearningHouseSecurityException as SecurityException
from learninghouse.api.errors.brain import (BrainNoConfiguration,
                                            BrainNotActual, BrainNotEnoughData,
                                            BrainNotTrained)
from learninghouse.models.brain import (BrainInfo, BrainPredictionRequest,
                                        BrainPredictionResult,
                                        BrainTrainingRequest)
from learninghouse.services.brain import Brain, BrainPrediction, BrainTraining

router = APIRouter(
    prefix='/brain',
    tags=['brain']
)


@router.get('/{name}/info',
            response_model=BrainInfo,
            summary='Retrieve information',
            description='Retrieve all information of a trained brain.',
            tags=['brain'],
            responses={
                200: {
                    'description': 'Information of the trained brain'
                },
                SecurityException.STATUS_CODE: SecurityException.api_description(),
                BrainNotTrained.STATUS_CODE: BrainNotTrained.api_description(),
                BrainNotActual.STATUS_CODE: BrainNotActual.api_description(),
                LearningHouseException.STATUS_CODE: LearningHouseException.api_description()
            })
async def info_get(name: str):
    brain_config = Brain.load_trained(name)
    return brain_config.info


@router.post('/{name}/training',
             response_model=BrainInfo,
             summary='Train the brain again',
             description='After version updates train the brain with existing data.',
             tags=['brain'],
             responses={
                 200: {
                     'description': 'Information of the trained brain'
                 },
                 SecurityException.STATUS_CODE: SecurityException.api_description(),
                 BrainNotEnoughData.STATUS_CODE: BrainNotEnoughData.api_description(),
                 BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.api_description(),
                 LearningHouseException.STATUS_CODE: LearningHouseException.api_description()
             })
async def training_post(name: str):
    return BrainTraining.request(name)


@router.put('/{name}/training',
            response_model=BrainInfo,
            summary='Train the brain with new data',
            description='Train the brain with additional data.',
            tags=['brain'],
            responses={
                200: {
                    'description': 'Information of the trained brain'
                },
                SecurityException.STATUS_CODE: SecurityException.api_description(),
                BrainNotEnoughData.STATUS_CODE: BrainNotEnoughData.api_description(),
                BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.api_description(),
                LearningHouseException.STATUS_CODE: LearningHouseException.api_description()
            })
async def training_put(name: str, request_data: BrainTrainingRequest):
    return BrainTraining.request(name, request_data.data)


@router.post('/{name}/prediction',
             response_model=BrainPredictionResult,
             summary='Prediction',
             description='Predict a new dataset with given brain.',
             tags=['brain'],
             responses={
                 200: {
                     'description': 'Prediction result'
                 },
                 SecurityException.STATUS_CODE: SecurityException.api_description(),
                 BrainNotActual.STATUS_CODE: BrainNotActual.api_description(),
                 BrainNotTrained.STATUS_CODE: BrainNotTrained.api_description(),
                 LearningHouseException.STATUS_CODE: LearningHouseException.api_description()
             })
async def prediction_post(name: str, request_data: BrainPredictionRequest):
    return BrainPrediction.prediction(name, request_data.data)
