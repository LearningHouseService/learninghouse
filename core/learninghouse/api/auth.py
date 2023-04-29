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
from learninghouse.services.auth import authservice


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
    return authservice.create_token(request.password)


@router.put("/token", response_model=Token)
async def put_token(refresh_token_jti: str = Depends(authservice.protect_refresh)):
    return authservice.refresh_token(refresh_token_jti)


@router.delete("/token", response_model=bool)
async def delete_token(
    refresh_token_jti: Union[str, None] = Depends(authservice.get_refresh)
):
    return authservice.revoke_refresh_token(refresh_token_jti)


router_protected = APIRouter(dependencies=[Depends(authservice.protect_admin)])


@router_protected.delete("/tokens", response_model=bool)
async def delete_tokens():
    return authservice.revoke_all_refresh_tokens()


@router_protected.put("/password", response_model=bool)
async def update_password(
    request: PasswordRequest, _=Depends(authservice.protect_admin)
):
    return authservice.update_password(request.old_password, request.new_password)


if not authservice.is_initial_admin_password:

    @router_protected.get("/apikeys", response_model=List[APIKeyInfo])
    async def list_api_keys():
        return authservice.list_api_keys()

    @router_protected.post("/apikey", response_model=APIKey)
    async def create_apikey(request: APIKeyRequest):
        return authservice.create_apikey(request)

    @router_protected.delete("/apikey/{description}", response_model=str)
    async def delete_apikey(
        description: str = Path(
            min_length=3,
            max_length=15,
            regex=r"^[A-Za-z]\w{1,13}[A-Za-z0-9]$",
            example="app_as_user",
        )
    ):
        return authservice.delete_apikey(description)


router.include_router(router_protected)


@router.get("/role", response_model=UserRole)
def role(user_role: UserRole = Depends(authservice.protect_user)):
    return user_role
