import uuid
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserUpdatePassword,
    UserUpdateRole,
)
from app.core.database import DbDep
from app.core.paging import Paging
from app.database.models.user import UserFilter
from app.database.repositories.user import UserRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)
        self.db = db

    async def create(self, user_create: UserCreate) -> uuid.UUID:
        user_by_email = await self.user_repository.get_by_email(user_create.email)
        if user_by_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        id = await self.user_repository.create(
            name=user_create.name,
            email=user_create.email,
            password=user_create.password,
            role=user_create.role,
        )
        await self.db.commit()
        return id

    async def get(self, user_id: uuid.UUID) -> UserResponse:
        user = await self.user_repository.get(user_id)
        return UserResponse.model_validate(user)

    async def get_many(self, paging: Paging, filter: UserFilter) -> list[UserResponse]:
        result = await self.user_repository.get_many(paging=paging, filter=filter)
        return [UserResponse.model_validate(user) for user in result]

    async def count(self, filter: UserFilter) -> int:
        return await self.user_repository.count(filter=filter)

    async def update(self, user_id: uuid.UUID, user_update: UserUpdate) -> None:
        await self.user_repository.update(user_id=user_id, user_update=user_update)
        await self.db.commit()

    async def update_password(
        self, user_id: uuid.UUID, user_update_password: UserUpdatePassword
    ) -> None:
        await self.user_repository.update_password(
            user_id, password=user_update_password.password
        )
        await self.db.commit()

    async def update_role(
        self, user_id: uuid.UUID, user_update_role: UserUpdateRole
    ) -> None:
        await self.user_repository.update_role(user_id, role=user_update_role.role)
        await self.db.commit()

    async def deactivate(self, user_id: uuid.UUID) -> None:
        user = await self.user_repository.get(user_id)
        if user.deleted_at:
            raise HTTPException(status_code=400, detail="User already deactivated")
        await self.user_repository.deactivate(user_id)
        await self.db.commit()

    async def reactivate(self, user_id: uuid.UUID) -> None:
        user = await self.user_repository.get(user_id)
        if not user.deleted_at:
            raise HTTPException(status_code=400, detail="User already reactivated")
        await self.user_repository.reactivate(user_id)
        await self.db.commit()

def get_user_service(db: DbDep) -> UserService:
    return UserService(db=db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
