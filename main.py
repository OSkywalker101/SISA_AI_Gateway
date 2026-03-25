from fastapi import FastAPI, Depends, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import pathlib

from config import settings
from gateway.middleware.auth import verify_api_key
from gateway.middleware.rate_limiter import get_rate_limiter
from gateway.middleware.logger import RequestLoggingMiddleware
from gateway.router.engine import router as llm_router
from gateway.analytics.db import init_db, log_request
from gateway.analytics.metrics import get_dashboard_metrics
from gateway.providers.base import ChatRequest

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init sqlite db
    await init_db()
    yield
    # Shutdown

app = FastAPI(title=settings.app_title, version=settings.app_version, lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# Serve dashboard static files
# We'll serve the dashboard html directly from a route instead of StaticFiles for simplicity

@app.get("/")
async def root_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard")

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.app_version}

@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatRequest,
    response: Response,
    fastapi_req: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Main Gateway Endpoint.
    1. Authenticates (Depends)
    2. Rate Limits
    3. Routes to best provider
    4. Logs to DB
    """
    # Rate limit check
    get_rate_limiter(api_key)
    
    # Route request (Engine applies rules, load balances, and executes)
    try:
        provider_resp = await llm_router.route(request)
        
        # Set headers for logger middleware and client
        response.headers["X-Gateway-Model"] = provider_resp.model
        response.headers["X-Gateway-Provider"] = provider_resp.provider
        
        # Estimate cost
        cost_per_1k = settings.models.get(provider_resp.model, {}).get("cost_per_1k_tokens", 0)
        cost_estimate = (provider_resp.total_tokens / 1000.0) * cost_per_1k
        
        # Async db log
        await log_request(
            api_key=api_key,
            model=provider_resp.model,
            provider=provider_resp.provider,
            status_code=200,
            latency_ms=provider_resp.latency_ms,
            prompt_tokens=provider_resp.prompt_tokens,
            completion_tokens=provider_resp.completion_tokens,
            cost_estimate_usd=cost_estimate
        )
        
        return provider_resp.model_dump()
        
    except Exception as e:
        # Log error
        await log_request(
            api_key=api_key,
            model=request.model,
            provider="unknown",
            status_code=500,
            latency_ms=0,
            error_msg=str(e)
        )
        raise

@app.get("/metrics")
async def metrics():
    """Returns analytics for the dashboard."""
    return await get_dashboard_metrics()

@app.get("/admin/routes")
async def get_routes():
    """Returns configured routing rules and models."""
    return {
        "models": settings.models,
        "task_type_routing": settings.task_type_routing,
        "cost_threshold_usd": settings.cost_threshold_usd
    }

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serves the admin dashboard HTML page."""
    dashboard_path = pathlib.Path(__file__).parent / "dashboard" / "index.html"
    if dashboard_path.exists():
        return dashboard_path.read_text(encoding="utf-8")
    return "<h1>Dashboard UI missing!</h1>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
