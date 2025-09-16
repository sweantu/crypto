import uuid
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import func, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.schemas.user import UserUpdate
from app.core.paging import Paging
from app.core.password import hash_password
from app.database.models.user import Role, User, UserFilter


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, name: str, email: str, password: str, role: Role
    ) -> uuid.UUID:
        stmt = (
            insert(User)
            .values(
                name=name,
                email=email,
                password=hash_password(password),
                role=role,
            )
            .returning(User.id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get(self, user_id: uuid.UUID) -> User:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_many(self, paging: Paging, filter: UserFilter) -> list[User]:
        stmt = select(User)
        stmt = filter.apply(stmt)
        stmt = paging.apply(stmt, User.created_at)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count(self, filter: UserFilter) -> int:
        stmt = select(func.count()).select_from(User)
        stmt = filter.apply(stmt)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def update(self, user_id: uuid.UUID, user_update: UserUpdate) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                name=user_update.name,
            )
        )
        await self.db.execute(stmt)

    async def update_password(self, user_id: uuid.UUID, password: str) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                password=hash_password(password),
            )
        )
        await self.db.execute(stmt)

    async def update_role(self, user_id: uuid.UUID, role: Role) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                role=role,
            )
        )
        await self.db.execute(stmt)

    async def deactivate(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                deleted_at=datetime.now(UTC),
            )
        )
        await self.db.execute(stmt)

    async def reactivate(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                deleted_at=None,
            )
        )
        await self.db.execute(stmt)
