from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED
from config import settings

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def verify_api_key(api_key_header: str = Security(api_key_header)):
    """Verifies that the provided API key is valid for this gateway."""
    if not api_key_header:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )
    
    # Allow Bearer token format
    if api_key_header.startswith("Bearer "):
        api_key_header = api_key_header[7:]

    if api_key_header not in settings.gateway_api_keys:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid or unauthorized API key",
        )
    
    return api_key_header
