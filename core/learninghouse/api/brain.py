from fastapi import APIRouter, Depends, status

from learninghouse.api.errors.brain import (
    BrainNoConfiguration,
    BrainNotActual,
    BrainNotEnoughData,
    BrainNotTrained,
    BrainExists
)
from learninghouse.models.brain import (
    BrainConfiguration,
    BrainDeleteResult,
    BrainInfo,
    BrainInfos,
    BrainPredictionRequest,
    BrainPredictionResult,
    BrainTrainingRequest,
)
from learninghouse.services.auth import authservice
from learninghouse.services.brain import BrainService, BrainConfigurationService


router = APIRouter(prefix="/brain", tags=["brain"])

router_usage = APIRouter(dependencies=[Depends(authservice.protect_user)])

router_training = APIRouter(
    dependencies=[Depends(authservice.protect_trainer)])

router_admin = APIRouter(dependencies=[Depends(authservice.protect_admin)])


@router_usage.get(
    "s/info",
    response_model=BrainInfos,
    summary="Retrieve information",
    description="Retrieve all information about brains.",
    responses={
        200: {"description": "Information of all brains"},
    },
)
async def infos_get():
    return BrainService.list_all()


@router_usage.get(
    "/{name}/info",
    response_model=BrainInfo,
    summary="Retrieve information",
    description="Retrieve all information of a brain.",
    responses={
        200: {"description": "Information of the brain"},
        BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.api_description(),
    },
)
async def info_get(name: str):
    return BrainService.get_info(name)


@router_training.post(
    "/{name}/training",
    response_model=BrainInfo,
    summary="Train the brain again",
    description="After version updates train the brain with existing data.",
    responses={
        200: {"description": "Information of the trained brain"},
        BrainNotEnoughData.STATUS_CODE: BrainNotEnoughData.api_description(),
        BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.api_description(),
    },
)
async def training_post(name: str):
    return BrainService.request(name)


@router_training.put(
    "/{name}/training",
    response_model=BrainInfo,
    summary="Train the brain with new data",
    description="Train the brain with additional data.",
    responses={
        200: {"description": "Information of the trained brain"},
        BrainNotEnoughData.STATUS_CODE: BrainNotEnoughData.api_description(),
        BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.api_description(),
    },
)
async def training_put(name: str, request: BrainTrainingRequest):
    return BrainService.request(name, request.dependent_value, request.sensors_data)


@router_usage.post(
    "/{name}/prediction",
    response_model=BrainPredictionResult,
    summary="Prediction",
    description="Predict a new dataset with given brain.",
    responses={
        200: {"description": "Prediction result"},
        BrainNotActual.STATUS_CODE: BrainNotActual.api_description(),
        BrainNotTrained.STATUS_CODE: BrainNotTrained.api_description(),
    },
)
async def prediction_post(name: str, request_data: BrainPredictionRequest):
    return BrainService.prediction(name, request_data.dict())


@router_usage.get(
    "/{name}/configuration",
    response_model=BrainConfiguration,
    summary="Get configuration of a brain",
    description="Get the configuration of the specified brain",
    responses={
        status.HTTP_200_OK: {"description": "Configuration of the brain"},
        BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.api_description(),
    },
)
async def configuration_get(name: str):
    return BrainConfigurationService.get(name)


@router_admin.post(
    "/configuration",
    response_model=BrainConfiguration,
    summary="Create a new brain configuration",
    description="Put the configuration of a new brain",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "The new brain was created"},
        BrainExists.STATUS_CODE: BrainExists.api_description(),
    },
)
async def configuration_post(brain: BrainConfiguration):
    return BrainConfigurationService.create(brain)


@router_admin.put(
    "/{name}/configuration",
    response_model=BrainConfiguration,
    summary="Update brain configuration",
    description="Post the configuration to update the brain",
    responses={
        status.HTTP_200_OK: {"description": "The brain configuration was updated"},
        BrainNoConfiguration.STATUS_CODE: BrainNoConfiguration.api_description(),
    },
)
async def configuration_put(name: str, configuration: BrainConfiguration):
    return BrainConfigurationService.update(name, configuration)


@router_admin.delete(
    "/{name}/configuration",
    response_model=BrainDeleteResult,
    summary="Delete whole brain",
    responses={status.HTTP_200_OK: {
        "description": "Returns the name of the brain"}},
)
async def configuration_delete(name: str):
    return BrainConfigurationService.delete(name)


router.include_router(router_usage)
router.include_router(router_training)
router.include_router(router_admin)
