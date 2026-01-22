import redis
import logging

logger = logging.getLogger(__name__)

# Flag to track if Redis is available
redis_available = False

try:
    redis_client = redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True,
        socket_connect_timeout=1  # Quick timeout for connection check
    )
    # Test the connection
    redis_client.ping()
    redis_available = True
    logger.info("Redis connection established successfully")
except (redis.ConnectionError, redis.TimeoutError) as e:
    logger.warning(f"Redis is not available: {e}. Rate limiting will be disabled.")
    redis_client = None
except Exception as e:
    logger.error(f"Unexpected error connecting to Redis: {e}. Rate limiting will be disabled.")
    redis_client = None
