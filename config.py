"""
AI Gateway – Configuration & Model Registry
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Gemini
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")

    # Gateway auth keys loaded from .env
    _raw_keys: str = os.getenv("GATEWAY_API_KEYS", "gw-test-key-123,gw-pro-key-456,gw-enterprise-key-789")
    _raw_tiers: str = os.getenv("KEY_TIERS", "gw-test-key-123:free,gw-pro-key-456:pro,gw-enterprise-key-789:enterprise")

    # Rate limits (requests per minute per tier)
    rate_limits: Dict[str, int] = {
        "free": 5,
        "pro": 30,
        "enterprise": 120,
    }

    # Model registry
    models: Dict[str, dict] = {
        "gemini-1.5-flash": {
            "provider": "gemini",
            "cost_per_1k_tokens": 0.00035,
            "priority": 1,
            "weight": 3,
            "tags": ["fast", "cheap", "default"],
        },
        "gemini-1.5-pro": {
            "provider": "gemini",
            "cost_per_1k_tokens": 0.0035,
            "priority": 2,
            "weight": 2,
            "tags": ["powerful", "reasoning", "code"],
        },
        "anthropic-claude-stub": {
            "provider": "anthropic",
            "cost_per_1k_tokens": 0.003,
            "priority": 3,
            "weight": 1,
            "tags": ["stub", "fallback"],
        },
        "openai-gpt4-stub": {
            "provider": "openai",
            "cost_per_1k_tokens": 0.03,
            "priority": 4,
            "weight": 1,
            "tags": ["stub", "expensive", "enterprise"],
        },
    }

    # Routing rules
    task_type_routing: Dict[str, str] = {
        "code": "gemini-1.5-pro",
        "summarize": "gemini-1.5-flash",
        "chat": "gemini-1.5-flash",
        "reasoning": "gemini-1.5-pro",
        "default": "gemini-1.5-flash",
    }

    # Cost threshold: if estimated cost > this (USD), route to cheaper model
    cost_threshold_usd: float = 0.01

    db_path: str = "gateway.db"
    app_title: str = "AI Gateway"
    app_version: str = "1.0.0"

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

    @property
    def gateway_api_keys(self) -> List[str]:
        return [k.strip() for k in self._raw_keys.split(",") if k.strip()]

    @property
    def key_tiers(self) -> Dict[str, str]:
        result = {}
        for pair in self._raw_tiers.split(","):
            if ":" in pair:
                k, v = pair.strip().split(":", 1)
                result[k.strip()] = v.strip()
        return result

    def get_tier(self, api_key: str) -> str:
        return self.key_tiers.get(api_key, "free")

    def get_rate_limit(self, api_key: str) -> int:
        tier = self.get_tier(api_key)
        return self.rate_limits.get(tier, 5)


settings = Settings()
