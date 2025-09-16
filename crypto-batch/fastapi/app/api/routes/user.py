from fastapi import APIRouter
from pydantic import UUID4

from app.api.schemas.user import UserResponse
from app.services.user import UserServiceDep

router = APIRouter()


@router.get("/{user_id}", response_model=UserResponse)
async def get(user_id: UUID4, user_service: UserServiceDep):
    return await user_service.get(user_id)
