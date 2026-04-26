from redis.asyncio import Redis

from app.core.redis import redis_client


async def get_redis() -> Redis:
    """Get the Redis client."""
    return await redis_client.get_redis()
