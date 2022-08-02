from fastapi import APIRouter, Depends

from learninghouse.api.errors.brain import (BrainNoConfiguration,
                                            BrainNotActual, BrainNotEnoughData,
                                            BrainNotTrained)
from learninghouse.models.brain import (BrainInfo, BrainPredictionRequest,
                                        BrainPredictionResult,
                                        BrainTrainingRequest)
from learninghouse.services.brain import Brain, BrainPrediction, BrainTraining
from learninghouse.services.auth import auth_service

auth = auth_service()

router = APIRouter(
    prefix='/brain',
    tags=['brain']
)

router_usage = APIRouter(
    dependencies=[Depends(auth.protect_user)]
)

router_training = APIRouter(
    dependencies=[Depends(auth.protect_trainer)]
)


@router_usage.get('/{name}/info',
                  response_model=BrainInfo,
                  summary='Retrieve information',
                  description='Retrieve all information of a trained brain.',
                  responses={
                      200: {
                          'description': 'Information of the trained brain'
                      },
                      BrainNotTrained.STATUS_CODE: BrainNotTrained.api_description()
                  })
async def info_get(name: str):
    brain_config = Brain.load_trained(name, False)
    return brain_config.info


@router_training.post('/{name}/training',
                      response_model=BrainInfo,
                      summary='Train the brain again',
                      description='After version updates train the brain with existing data.',
                      responses={
                          200: {
                              'description': 'Information of the trained brain'
                          },
                          BrainNotEnoughData.STATUS_CODE: BrainNotEnoughData.api_description(),
                          BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.api_description()
                      })
async def training_post(name: str):
    return BrainTraining.request(name)


@router_training.put('/{name}/training',
                     response_model=BrainInfo,
                     summary='Train the brain with new data',
                     description='Train the brain with additional data.',
                     responses={
                         200: {
                             'description': 'Information of the trained brain'
                         },
                         BrainNotEnoughData.STATUS_CODE: BrainNotEnoughData.api_description(),
                         BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.api_description()
                     })
async def training_put(name: str, request_data: BrainTrainingRequest):
    return BrainTraining.request(name, request_data.dict())


@router_usage.post('/{name}/prediction',
                   response_model=BrainPredictionResult,
                   summary='Prediction',
                   description='Predict a new dataset with given brain.',
                   responses={
                       200: {
                           'description': 'Prediction result'
                       },
                       BrainNotActual.STATUS_CODE: BrainNotActual.api_description(),
                       BrainNotTrained.STATUS_CODE: BrainNotTrained.api_description()
                   })
async def prediction_post(name: str, request_data: BrainPredictionRequest):
    return BrainPrediction.prediction(name, request_data.dict())

router.include_router(router_usage)
router.include_router(router_training)
