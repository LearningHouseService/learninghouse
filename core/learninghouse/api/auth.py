from typing import List, Union

from fastapi import APIRouter, Depends, Path

from learninghouse.api.errors.auth import InvalidPassword
from learninghouse.models.auth import (
    APIKey,
    APIKeyInfo,
    APIKeyRequest,
    LoginRequest,
    PasswordRequest,
    Token,
    UserRole,
)
from learninghouse.services.auth import auth_service

auth = auth_service()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/token",
    response_model=Token,
    responses={
        200: {"description": "Successfully retrieve token"},
        InvalidPassword.STATUS_CODE: InvalidPassword.api_description(),
    },
)
async def post_token(request: LoginRequest):
    return auth.create_token(request.password)


@router.put("/token", response_model=Token)
async def put_token(refresh_token_jti: str = Depends(auth.protect_refresh)):
    return auth.refresh_token(refresh_token_jti)


@router.delete("/token", response_model=bool)
async def delete_token(refresh_token_jti: Union[str, None] = Depends(auth.get_refresh)):
    return auth.revoke_refresh_token(refresh_token_jti)


router_protected = APIRouter(dependencies=[Depends(auth.protect_admin)])


@router_protected.delete("/tokens", response_model=bool)
async def delete_tokens():
    return auth.revoke_all_refresh_tokens()


@router_protected.put("/password", response_model=bool)
async def update_password(request: PasswordRequest, _=Depends(auth.protect_admin)):
    return auth.update_password(request.old_password, request.new_password)


if not auth.is_initial_admin_password:

    @router_protected.get("/apikeys", response_model=List[APIKeyInfo])
    async def list_api_keys():
        return auth.list_api_keys()

    @router_protected.post("/apikey", response_model=APIKey)
    async def create_apikey(request: APIKeyRequest):
        return auth.create_apikey(request)

    @router_protected.delete("/apikey/{description}", response_model=str)
    async def delete_apikey(
        description: str = Path(
            min_length=3,
            max_length=15,
            regex=r"^[A-Za-z]\w{1,13}[A-Za-z0-9]$",
            example="app_as_user",
        )
    ):
        return auth.delete_apikey(description)


router.include_router(router_protected)


@router.get("/role", response_model=UserRole)
def role(user_role: UserRole = Depends(auth.protect_user)):
    return user_role
