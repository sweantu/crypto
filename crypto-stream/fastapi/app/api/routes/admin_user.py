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
from app.core.redis_core import RedisCoreDep
from app.database.models.user import Role, UserFilter
from app.services.user import UserServiceDep

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create(
    user_create: UserCreate,
    user_service: UserServiceDep,
    redis_core: RedisCoreDep,
):
    id = await user_service.create(user_create)
    response = await user_service.get(user_id=id)

    cache_key = "users"
    await redis_core.clear(cache_key)
    return response


@router.get("/{user_id}", response_model=UserResponse)
async def get(user_id: UUID4, user_service: UserServiceDep):
    return await user_service.get(user_id)


@router.get("/", response_model=PagingResponse[UserResponse])
async def get_many(
    user_service: UserServiceDep,
    paging: PagingDep,
    redis_core: RedisCoreDep,
    search_text: str = Query(None),
    role: Annotated[Role | None, Query()] = None,
    is_deleted: bool | None = Query(None),
):
    cache_key = "users"
    cache_field = f"p{paging.page}:s{paging.page_size}:o{paging.sort}:st{search_text}:r{role}:d{is_deleted}"
    cached_data = await redis_core.get(cache_key, cache_field)
    if cached_data:
        response = PagingResponse[UserResponse].model_validate_json(cached_data)
        response.cached = True
        return response

    filter = UserFilter(search_text=search_text, role=role, is_deleted=is_deleted)
    items = await user_service.get_many(paging=paging, filter=filter)
    total = await user_service.count(filter=filter)
    response = PagingResponse[UserResponse](
        total=total, page=paging.page, page_size=paging.page_size, items=items
    )

    await redis_core.set(cache_key, cache_field, response.model_dump_json())
    return response


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

@router.delete("/cache")
async def delete_users_cache(redis_core: RedisCoreDep):
    cache_key = "users"
    await redis_core.clear(cache_key)
    return {"message": "Cache cleared"}