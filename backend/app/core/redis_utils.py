

from redis.asyncio import Redis
from app.core.config import settings
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Optional

class RedisClient:
    """Redis client for real-time processing"""

    def __init__(self):
        self.client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def publish(self, channel: str, message: str) -> None:
        """
        Publish message to a Redis channel
        
        Args:
            channel: Redis channel name
            message: Message to publish
        """
        try:
            await self.client.publish(channel, message)
            logger.info(f"Published message to {channel}")
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")
            raise

    async def subscribe(self, channel: str) -> None:
        """
        Subscribe to a Redis channel (placeholder for frontend integration)
        
        Args:
            channel: Redis channel name
        """
        try:
            pubsub = self.client.pubsub()
            await pubsub.subscribe(channel)
            logger.info(f"Subscribed to {channel}")
            # Placeholder: Handle messages in frontend
        except Exception as e:
            logger.error(f"Failed to subscribe to {channel}: {e}")
            raise

    async def close(self) -> None:
        """Close Redis connection"""
        try:
            await self.client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Failed to close Redis connection: {e}")
            raise

async def get_redis_client() -> RedisClient:
    """Dependency for RedisClient"""
    return RedisClient()
