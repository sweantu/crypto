import os
from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

REDIS_HOST = os.getenv("REDIS_HOST", "")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
ENV = os.getenv("ENV", "local")
r = Redis(host=REDIS_HOST, port=int(REDIS_PORT), decode_responses=False)


class RedisCore:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    def _generate_redis_key(self, key: str) -> str:
        return f"recommendation:{ENV}:{key}"

    async def set(self, key: str, field: str, value: str, expiry: int = 300):
        full_key = self._generate_redis_key(key)
        await r.hset(full_key, field, value)  # type: ignore
        if expiry > 0:
            await r.expire(full_key, expiry)

    async def get(self, key: str, field: str) -> str | None:
        full_key = self._generate_redis_key(key)
        return await r.hget(full_key, field)  # type: ignore

    async def delete(self, key: str, field: str):
        full_key = self._generate_redis_key(key)
        await r.hdel(full_key, field)  # type: ignore

    async def clear(self, key: str):
        full_key = self._generate_redis_key(key)
        await r.delete(full_key)


redis_core = RedisCore(r)


def get_redis_core() -> RedisCore:
    return redis_core


RedisCoreDep = Annotated[RedisCore, Depends(get_redis_core)]
