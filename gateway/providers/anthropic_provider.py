import time
import uuid
import asyncio
from gateway.providers.base import BaseProvider, ChatRequest, ProviderResponse

class AnthropicStubProvider(BaseProvider):
    provider_name = "anthropic"

    async def complete(self, request: ChatRequest, model_name: str) -> ProviderResponse:
        """Simulate an Anthropic Claude API call."""
        start_time = time.time()
        
        prompt = request.messages[-1].content if request.messages else "Hello"
        mock_response = f"[Anthropic Stub] Claude here. I am a mocked {model_name} processing your query: '{prompt[:50]}...'"
        
        await asyncio.sleep(0.5) # simulate delay
        
        latency = (time.time() - start_time) * 1000
        prompt_tokens = len(prompt.split()) * 1.5
        comp_tokens = len(mock_response.split()) * 1.5
        
        return ProviderResponse(
            id=f"msg-{uuid.uuid4().hex[:12]}",
            model=model_name,
            provider=self.provider_name,
            content=mock_response,
            prompt_tokens=int(prompt_tokens),
            completion_tokens=int(comp_tokens),
            total_tokens=int(prompt_tokens + comp_tokens),
            latency_ms=latency
        )

    async def is_healthy(self) -> bool:
        return True
