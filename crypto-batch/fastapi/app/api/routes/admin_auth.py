from fastapi import APIRouter

from app.api.schemas.auth import AuthResponse, Login
from app.api.schemas.user import UserResponse, UserUpdate, UserUpdatePassword
from app.core.auth import AdminAuthPayloadDep
from app.database.models.user import Role
from app.services.auth import AuthServiceDep
from app.services.user import UserServiceDep
from app.validations.access import validate_role_access

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
async def login(
    login: Login,
    auth_service: AuthServiceDep,
):
    result = await auth_service.login(email=login.email, password=login.password)
    validate_role_access(roles=[Role.ADMIN], user_role=result.user.role)
    return result


@router.get("/me", response_model=UserResponse)
async def get_me(auth_payload: AdminAuthPayloadDep, user_service: UserServiceDep):
    result = await user_service.get(auth_payload.user_id)
    return result


@router.put("/", response_model=UserResponse)
async def update(
    auth_payload: AdminAuthPayloadDep,
    user_update: UserUpdate,
    user_service: UserServiceDep,
):
    await user_service.update(user_id=auth_payload.user_id, user_update=user_update)
    return await user_service.get(user_id=auth_payload.user_id)


@router.put("/password", response_model=UserResponse)
async def update_password(
    auth_payload: AdminAuthPayloadDep,
    user_update_password: UserUpdatePassword,
    user_service: UserServiceDep,
):
    await user_service.update_password(
        user_id=auth_payload.user_id, user_update_password=user_update_password
    )
    return await user_service.get(user_id=auth_payload.user_id)
