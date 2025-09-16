import uuid

from fastapi import HTTPException

from app.database.models.user import Role


def validate_access(owner_id: uuid.UUID, user_id: uuid.UUID) -> None:
    if owner_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")


def validate_role_access(roles: list[Role], user_role: Role) -> None:
    if user_role not in roles:
        raise HTTPException(status_code=403, detail="Access denied")
