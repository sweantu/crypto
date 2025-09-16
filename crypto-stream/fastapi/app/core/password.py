from fastapi import HTTPException
from passlib.context import CryptContext

# Configure hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    if not pwd_context.verify(plain_password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
