import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import json

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Read request body to estimate tokens (simplified)
        body = b""
        if request.method == "POST":
            body = await request.body()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Extract metadata from response headers set by router
        model_used = response.headers.get("X-Gateway-Model", "unknown")
        provider = response.headers.get("X-Gateway-Provider", "unknown")
        
        # Determine API key for logging
        auth_header = request.headers.get("Authorization", "")
        api_key = auth_header.replace("Bearer ", "") if "Bearer" in auth_header else "unknown"

        # Note: in a real app we'd log this to SQLite using `analytics.db` module asynchronously.
        # For now, we do standard output logging to console.
        print(f"[{request.method}] {request.url.path} | Key: {api_key[:5]}*** | Time: {process_time:.3f}s | Model: {model_used} | Status: {response.status_code}")
        
        return response
