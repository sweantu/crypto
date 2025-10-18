import os
from typing import Annotated

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL = os.getenv("POSTGRES_URI", "")
engine = create_async_engine(
    DATABASE_URL.replace(
        "postgresql+psycopg2", "postgresql+asyncpg"
    ),  # Ensure asyncpg driver
    pool_pre_ping=True,
    echo=False,  # Set to True for debugging
)

SessionLocal = async_sessionmaker(
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
)

Base = declarative_base()


async def health_check():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}


async def get_db():
    async with SessionLocal() as session:
        yield session
        # get a connection from the pool, automatically open a transaction when running a first query, if you don't commit manually, it will automatically rollback. One connection can have multiple transactions during its lifetime.


DbDep = Annotated[AsyncSession, Depends(get_db)]
