import redis.asyncio as redis

from .config import redis_config


class RedisClient:
    def __init__(self) -> None:
        self.redis = redis.Redis(
            host=redis_config.host,
            port=redis_config.port,
            decode_responses=True,
        )

    async def set(self, key: str, value: str, expiration: int = 3600) -> None:
        await self.redis.set(key, value, ex=expiration)

    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)


redis_client = RedisClient()
