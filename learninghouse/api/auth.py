from typing import List

from fastapi import APIRouter, Depends, Path

from learninghouse.models.auth import (APIKey, APIKeyInfo, APIKeyRequest,
                                       LoginRequest, PasswordRequest, Token)
from learninghouse.services.auth import auth_service

auth = auth_service()

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post('/login',
             response_model=Token)
async def login(request: LoginRequest):
    return auth.login(request.password)

router_protected = APIRouter(
    dependencies=[Depends(auth.protect_admin)]
)


@router_protected.put('/password', response_model=bool)
async def update_password(request: PasswordRequest, _=Depends(auth.protect_admin)):
    return auth.update_password(request.old_password, request.new_password)

if not auth.is_initial_admin_password:
    @router_protected.get('/apikeys', response_model=List[APIKeyInfo])
    async def list_api_keys():
        return auth.list_api_keys()

    @router_protected.post('/apikey', response_model=APIKey)
    async def create_apikey(request: APIKeyRequest):
        return auth.create_apikey(request)

    @router_protected.delete('/apikey/{description}', response_model=str)
    async def delete_apikey(description: str = Path(None,
                                                    min_length=3,
                                                    max_length=15,
                                                    regex='^[a-z][a-z_]{1,13}[a-z]$',
                                                    example='app_as_user')):
        return auth.delete_apikey(description)

router.include_router(router_protected)
