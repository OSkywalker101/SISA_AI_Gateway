import aiosqlite
from config import settings
import time
import asyncio

async def init_db():
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                api_key str,
                model str,
                provider str,
                status_code INTEGER,
                latency_ms REAL,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                cost_estimate_usd REAL,
                error_msg TEXT
            )
        ''')
        await db.commit()

async def log_request(
    api_key: str, 
    model: str, 
    provider: str, 
    status_code: int, 
    latency_ms: float, 
    prompt_tokens: int = 0, 
    completion_tokens: int = 0, 
    cost_estimate_usd: float = 0.0,
    error_msg: str = None
):
    """Log a completed API request to SQLite."""
    try:
        async with aiosqlite.connect(settings.db_path) as db:
            await db.execute('''
                INSERT INTO requests (
                    timestamp, api_key, model, provider, status_code, 
                    latency_ms, prompt_tokens, completion_tokens, cost_estimate_usd, error_msg
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                time.time(), api_key, model, provider, status_code, 
                latency_ms, prompt_tokens, completion_tokens, cost_estimate_usd, error_msg
            ))
            await db.commit()
    except Exception as e:
        print(f"Failed to log request to DB: {e}")

# Run init on import (will be awaited in main startup event)
