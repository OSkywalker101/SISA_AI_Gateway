import time
import uuid
import asyncio
from gateway.providers.base import BaseProvider, ChatRequest, ProviderResponse

class OpenAIStubProvider(BaseProvider):
    provider_name = "openai"

    async def complete(self, request: ChatRequest, model_name: str) -> ProviderResponse:
        """Simulate an OpenAI GPT-4 API call."""
        start_time = time.time()
        
        # Simulate network latency based on text size (30-80ms per token approx)
        prompt = request.messages[-1].content if request.messages else "Hello"
        mock_response = f"[OpenAI Stub] This is a mocked response from {model_name}. I received your prompt: '{prompt[:50]}...'"
        
        await asyncio.sleep(0.8) # simulate delay
        
        latency = (time.time() - start_time) * 1000
        prompt_tokens = len(prompt.split()) * 2
        comp_tokens = len(mock_response.split()) * 2
        
        return ProviderResponse(
            id=f"chatcmpl-{uuid.uuid4().hex}",
            model=model_name,
            provider=self.provider_name,
            content=mock_response,
            prompt_tokens=prompt_tokens,
            completion_tokens=comp_tokens,
            total_tokens=prompt_tokens + comp_tokens,
            latency_ms=latency
        )

    async def is_healthy(self) -> bool:
        return True
