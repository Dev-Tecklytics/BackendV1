from fastapi import HTTPException, status
from app.core.redis_client import redis_client

RATE_LIMIT = 60 # requests
WINDOW_SECONDS = 60 # per minute

def enforce_rate_limit(api_key_id: str):
    key = f"rate_limit:{api_key_id}"

    current_count = redis_client.incr(key)

    if current_count == 1:
        # first request → set expiry
        redis_client.expire(key, WINDOW_SECONDS)

    if current_count > RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later."
        )
