from fastapi import HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from config import settings
import time
from typing import Dict, Tuple

# Simple in-memory token bucket rate limiter
# Format: {api_key: (tokens, last_refill_time)}
buckets: Dict[str, Tuple[float, float]] = {}

def get_rate_limiter(api_key: str):
    """Token bucket rate limiting logic per API key."""
    now = time.time()
    limit = settings.get_rate_limit(api_key)
    # Refill rate: limit per 60 seconds
    refill_rate = limit / 60.0 

    if api_key not in buckets:
        buckets[api_key] = (limit - 1, now)
        return True

    tokens, last_refill = buckets[api_key]
    
    # Calculate token refill
    elapsed = now - last_refill
    tokens += elapsed * refill_rate
    if tokens > limit:
        tokens = limit

    if tokens >= 1:
        buckets[api_key] = (tokens - 1, now)
        return True
    
    raise HTTPException(
        status_code=HTTP_429_TOO_MANY_REQUESTS,
        detail=f"Rate limit exceeded for tier '{settings.get_tier(api_key)}'. Limit is {limit} req/min.",
        headers={"Retry-After": str(int(1 / refill_rate))}
    )
