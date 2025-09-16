from datetime import datetime

from pydantic import UUID4, BaseModel, EmailStr

from app.database.models.user import Role


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Role

class UserResponse(BaseModel):
    id: UUID4
    name: str
    email: EmailStr
    role: Role
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    class Config:
        from_attributes = True

class UserUpdatePassword(BaseModel):
    password: str


class UserUpdateRole(BaseModel):
    role: Role


class UserUpdate(BaseModel):
    name: str
