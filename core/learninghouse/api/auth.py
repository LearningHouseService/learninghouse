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
from learninghouse.services.auth import (
    AuthServiceInternal,
    auth_service_cached,
    get_refresh,
    protect_admin,
    protect_refresh,
    protect_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/token",
    response_model=Token,
    responses={
        200: {"description": "Successfully retrieve token"},
        InvalidPassword.STATUS_CODE: InvalidPassword.api_description(),
    },
)
async def post_token(
    request: LoginRequest,
    auth_service: AuthServiceInternal = Depends(auth_service_cached),
):
    return auth_service.create_token(request.password)


@router.put("/token", response_model=Token)
async def put_token(
    refresh_token_jti: str = Depends(protect_refresh),
    auth_service: AuthServiceInternal = Depends(auth_service_cached),
):
    return auth_service.refresh_token(refresh_token_jti)


@router.delete("/token", response_model=bool)
async def delete_token(
    refresh_token_jti: Union[str, None] = Depends(get_refresh),
    auth_service: AuthServiceInternal = Depends(auth_service_cached),
):
    return auth_service.revoke_refresh_token(refresh_token_jti)


router_protected = APIRouter(dependencies=[Depends(protect_admin)])


@router_protected.delete("/tokens", response_model=bool)
async def delete_tokens(
    auth_service: AuthServiceInternal = Depends(auth_service_cached),
):
    return auth_service.revoke_all_refresh_tokens()


@router_protected.put("/password", response_model=bool)
async def update_password(
    request: PasswordRequest,
    auth_service: AuthServiceInternal = Depends(auth_service_cached),
):
    return auth_service.update_password(request.old_password, request.new_password)


# Registered unconditionally: EnforceInitialPasswordChange already blocks every
# non-allowlisted endpoint, including these, while the admin password is still
# the initial one. Gating registration itself on that same flag at import time
# used to mean these routes stayed 404 forever after the first request in the
# process saw an initial password - changing the password did not bring them
# back without a full restart.
@router_protected.get("/apikeys", response_model=List[APIKeyInfo])
async def list_api_keys(
    auth_service: AuthServiceInternal = Depends(auth_service_cached),
):
    return auth_service.list_api_keys()


@router_protected.post("/apikey", response_model=APIKey)
async def create_apikey(
    request: APIKeyRequest,
    auth_service: AuthServiceInternal = Depends(auth_service_cached),
):
    return auth_service.create_apikey(request)


@router_protected.delete("/apikey/{description}", response_model=str)
async def delete_apikey(
    description: str = Path(
        min_length=3,
        max_length=15,
        pattern=r"^[A-Za-z]\w{1,13}[A-Za-z0-9]$",
        examples=["app_as_user"],
    ),
    auth_service: AuthServiceInternal = Depends(auth_service_cached),
):
    return auth_service.delete_apikey(description)


router.include_router(router_protected)


@router.get("/role", response_model=UserRole)
def role(user_role: UserRole = Depends(protect_user)):
    return user_role
