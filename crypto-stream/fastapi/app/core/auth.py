import os
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import UUID4, BaseModel

from app.database.models.user import Role

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


class AuthPayload(BaseModel):
    user_id: UUID4
    role: Role


class OptionalAuthPayload(BaseModel):
    user_id: UUID4 | None = None


def create_access_token(user_id: str, role: Role) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"user_id": user_id, "role": role, "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> AuthPayload:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        payload["user_id"] = uuid.UUID(payload["user_id"])
        return AuthPayload(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        ) from e


def get_auth_payload_with_roles(roles: list[Role] | None = None):
    def _get_auth_payload(
        auth_payload: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    ) -> AuthPayload:
        payload = decode_access_token(auth_payload.credentials)
        if roles and payload.role not in roles:
            raise HTTPException(
                status_code=403,
                detail="Access denied",
            )
        return payload

    return Depends(_get_auth_payload)


def get_optional_auth_payload(
    auth_payload: Annotated[
        HTTPAuthorizationCredentials | None, Depends(HTTPBearer(auto_error=False))
    ],
) -> OptionalAuthPayload:
    if not auth_payload:
        return OptionalAuthPayload()
    payload = decode_access_token(auth_payload.credentials)
    return OptionalAuthPayload(**payload.model_dump())


AuthPayloadDep = Annotated[AuthPayload, get_auth_payload_with_roles([Role.USER])]
AdminAuthPayloadDep = Annotated[AuthPayload, get_auth_payload_with_roles([Role.ADMIN])]

OptionalAuthPayloadDep = Annotated[
    OptionalAuthPayload, Depends(get_optional_auth_payload)
]
