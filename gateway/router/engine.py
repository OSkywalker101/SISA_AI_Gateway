import time
from fastapi import HTTPException
from gateway.providers.base import ChatRequest, ProviderResponse
from gateway.router.rules import select_model
from gateway.router.load_balancer import balancer
from gateway.providers.registry import get_provider_instance
from config import settings

class RouterEngine:
    async def route(self, request: ChatRequest) -> ProviderResponse:
        """Core routing logic: Rule evaluation -> LB -> Execute -> Fallback."""
        
        # 1. Apply rules to select target model
        target_model = select_model(request)
        
        # 2. Extract provider using LB
        model_name, provider_name = balancer.get_next_provider_for_model(target_model)
        
        # 3. Get provider instance
        provider = get_provider_instance(provider_name)
        
        # 4. Execute with fallback retry logic
        try:
            # If provider is completely unavailable/offline beforehand
            if not await provider.is_healthy():
                raise ConnectionError(f"Provider {provider_name} is unhealthy.")
                
            response = await provider.complete(request, model_name)
            return response
            
        except Exception as e:
            print(f"Primary model {target_model} failed: {e}. Attempting fallback...")
            
            # Fallback to the lowest priority (usually a stub or cheapest model)
            # Find cheapest fallback that is not the failed model
            fallbacks = [m for m, cfg in settings.models.items() if m != target_model and "fallback" in cfg.get("tags", [])]
            fallback_model = fallbacks[0] if fallbacks else "gemini-1.5-flash"
            
            fb_provider_name = settings.models[fallback_model]["provider"]
            fb_provider = get_provider_instance(fb_provider_name)
            
            try:
                response = await fb_provider.complete(request, fallback_model)
                # Mark as fallback in response ID
                response.id = f"fallback-{response.id}"
                return response
            except Exception as fallback_err:
                raise HTTPException(status_code=502, detail=f"All routes failed. Fallback error: {str(fallback_err)}")

router = RouterEngine()
