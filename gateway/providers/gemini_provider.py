import google.generativeai as genai
import time
import uuid
from gateway.providers.base import BaseProvider, ChatRequest, ProviderResponse
from config import settings

class GeminiProvider(BaseProvider):
    provider_name = "gemini"

    def __init__(self):
        # Configure Gemini API
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self._available = True
        else:
            self._available = False

    async def complete(self, request: ChatRequest, model_name: str) -> ProviderResponse:
        if not self._available:
            raise ValueError("Gemini API key is not configured.")

        start_time = time.time()
        
        # Instantiate the model
        model = genai.GenerativeModel(model_name)
        
        # Convert standard messages to Gemini format
        # Gemini expects: [{'role': 'user', 'parts': ['Hello']}]
        history = []
        for msg in request.messages:
            role = "user" if msg.role == "user" else "model"
            history.append({"role": role, "parts": [msg.content]})
            
        # Extract the last user message for the `generate_content` call
        # Or alternatively just use start_chat(history=...)
        prompt = history[-1]["parts"][0]
        recent_history = history[:-1] if len(history) > 1 else None

        try:
            if recent_history:
                chat = model.start_chat(history=recent_history)
                response = chat.send_message(prompt)
            else:
                response = model.generate_content(prompt)

            latency = (time.time() - start_time) * 1000
            
            # Approximate token counts (Gemini provides metadata in response.usage_metadata, but we'll use a simple proxy if missing)
            prompt_tokens_count = 0
            completion_tokens_count = 0
            if hasattr(response, "usage_metadata"):
                prompt_tokens_count = getattr(response.usage_metadata, "prompt_token_count", 0)
                completion_tokens_count = getattr(response.usage_metadata, "candidates_token_count", 0)
            
            # Simple approximation if metadata is absent
            if prompt_tokens_count == 0:
                prompt_tokens_count = len(prompt.split()) * 1.3
                completion_tokens_count = len(response.text.split()) * 1.3
                
            return ProviderResponse(
                id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
                model=model_name,
                provider=self.provider_name,
                content=response.text,
                prompt_tokens=int(prompt_tokens_count),
                completion_tokens=int(completion_tokens_count),
                total_tokens=int(prompt_tokens_count + completion_tokens_count),
                latency_ms=latency
            )
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")

    async def is_healthy(self) -> bool:
        return self._available
