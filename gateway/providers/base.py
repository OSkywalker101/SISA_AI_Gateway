from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "auto"
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: Optional[int] = None

class ProviderResponse(BaseModel):
    id: str
    model: str
    provider: str
    content: str
    role: str = "assistant"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0

class BaseProvider(ABC):
    provider_name: str

    @abstractmethod
    async def complete(self, request: ChatRequest, model_name: str) -> ProviderResponse:
        """Execute a chat completion request to the provider."""
        pass

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Check if provider connection is healthy."""
        pass
