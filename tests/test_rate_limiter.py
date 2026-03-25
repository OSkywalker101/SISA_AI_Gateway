import pytest
from fastapi import HTTPException
from gateway.middleware.rate_limiter import get_rate_limiter, buckets
from config import settings

def test_rate_limiter_allows_under_limit():
    key = "gw-test-key-123" # Free tier (5 req/min)
    if key in buckets:
        del buckets[key]
        
    # Should allow 5 requests
    for _ in range(5):
        assert get_rate_limiter(key) is True

def test_rate_limiter_blocks_over_limit():
    key = "gw-test-key-123"
    if key in buckets:
        del buckets[key]
        
    # Burn through the tokens
    for _ in range(5):
        get_rate_limiter(key)
        
    # 6th should fail
    with pytest.raises(HTTPException) as exc:
        get_rate_limiter(key)
        
    assert exc.value.status_code == 429
    assert "Rate limit exceeded" in exc.value.detail
