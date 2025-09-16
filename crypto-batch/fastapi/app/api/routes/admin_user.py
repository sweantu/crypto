from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import UUID4

from app.api.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdatePassword,
    UserUpdateRole,
)
from app.core.paging import PagingDep, PagingResponse
from app.database.models.user import Role, UserFilter
from app.services.user import UserServiceDep

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create(user_create: UserCreate, user_service: UserServiceDep):
    id = await user_service.create(user_create)
    return await user_service.get(user_id=id)


@router.get("/{user_id}", response_model=UserResponse)
async def get(user_id: UUID4, user_service: UserServiceDep):
    return await user_service.get(user_id)


@router.get("/", response_model=PagingResponse[UserResponse])
async def get_many(
    user_service: UserServiceDep,
    paging: PagingDep,
    search_text: str = Query(None),
    role: Annotated[Role | None, Query()] = None,
    is_deleted: bool | None = Query(None),
):
    filter = UserFilter(search_text=search_text, role=role, is_deleted=is_deleted)
    items = await user_service.get_many(paging=paging, filter=filter)
    total = await user_service.count(filter=filter)
    return PagingResponse[UserResponse](
        total=total, page=paging.page, page_size=paging.page_size, items=items
    )


@router.put("/{user_id}/password", response_model=UserResponse)
async def update_password(
    user_id: UUID4,
    user_update_password: UserUpdatePassword,
    user_service: UserServiceDep,
):
    await user_service.update_password(user_id, user_update_password)
    return await user_service.get(user_id=user_id)


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_role(
    user_id: UUID4,
    user_update_role: UserUpdateRole,
    user_service: UserServiceDep,
):
    await user_service.update_role(user_id, user_update_role)
    return await user_service.get(user_id=user_id)


@router.put("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate(user_id: UUID4, user_service: UserServiceDep):
    await user_service.deactivate(user_id)
    return await user_service.get(user_id=user_id)


@router.put("/{user_id}/reactivate", response_model=UserResponse)
async def reactivate(user_id: UUID4, user_service: UserServiceDep):
    await user_service.reactivate(user_id)
    return await user_service.get(user_id=user_id)
