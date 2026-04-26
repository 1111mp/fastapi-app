import redis.asyncio as redis
import structlog

logger = structlog.get_logger("redis")


class RedisClient:
    """Redis client wrapper for asyncio."""

    def __init__(self):
        self.client: redis.Redis | None = None

    async def init(self, url: str):
        """Initialize the Redis client from the given URL."""

        logger.info("Initializing Redis client")
        self.client = redis.Redis.from_url(
            url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=10,
        )
        logger.info("Redis client initialized")
        await self.client.ping()  # type: ignore
        logger.info("Redis client connected")

    async def close(self):
        """Close the Redis connection."""
        if self.client:
            await self.client.close(True)
            logger.info("Redis client closed")

    async def get_redis(self) -> redis.Redis:
        """Return the Redis client instance."""
        assert self.client is not None, "Redis not initialized"
        return self.client


redis_client = RedisClient()
