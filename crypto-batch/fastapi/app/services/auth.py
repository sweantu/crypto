from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.auth import AuthResponse, Register
from app.api.schemas.user import UserResponse
from app.core.auth import create_access_token
from app.core.database import DbDep
from app.core.password import verify_password
from app.database.models.user import Role
from app.database.repositories.user import UserRepository


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)
        self.db = db

    async def login(self, email: str, password: str) -> AuthResponse:
        user = await self.user_repository.get_by_email(email)
        if not user or not user.password:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )
        verify_password(password, user.password)
        access_token = create_access_token(user_id=str(user.id), role=user.role)
        return AuthResponse(
            access_token=access_token, user=UserResponse.model_validate(user)
        )

    async def register(self, register: Register) -> None:
        user_by_email = await self.user_repository.get_by_email(email=register.email)
        if user_by_email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )
        await self.user_repository.create(
            name=register.name,
            email=register.email,
            password=register.password,
            role=Role.USER,
        )
        await self.db.commit()


def get_auth_service(db: DbDep) -> AuthService:
    return AuthService(db=db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
