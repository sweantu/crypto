import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from sqlalchemy import DateTime, Select, String, func, or_, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(100), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # DB-side default for INSERT
        onupdate=func.now(),  # ORM auto-update for UPDATE
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class UserFilter(BaseModel):
    search_text: str | None = None
    role: Role | None = None
    is_deleted: bool | None = None

    def apply(self, stmt: Select) -> Select:
        conditions = []
        if self.search_text:
            conditions.append(
                or_(
                    User.email.ilike(f"%{self.search_text}%"),
                    User.name.ilike(f"%{self.search_text}%"),
                )
            )
        if self.role:
            conditions.append(User.role == self.role)

        if self.is_deleted is not None:
            conditions.append(
                User.deleted_at.isnot(None)
                if self.is_deleted
                else User.deleted_at.is_(None)
            )

        if conditions:
            stmt = stmt.where(*conditions)
        return stmt
