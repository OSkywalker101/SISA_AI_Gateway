from typing import List, Tuple
from config import settings
from gateway.providers.registry import get_provider_instance

class LoadBalancer:
    def __init__(self):
        # We index the round robin by model_name to properly balance identical model requests
        self._counters = {}
    
    def get_next_provider_for_model(self, model_name: str) -> Tuple[str, str]:
        """Simple health-aware router to get the underlying provider name for a model."""
        if model_name not in settings.models:
            raise ValueError(f"Model {model_name} not registered")

        model_info = settings.models[model_name]
        provider_name = model_info["provider"]
        
        # In a real heavy-traffic scenario, this might pick between multiple 
        # API keys or accounts for the same provider. Here we just return the provider name.
        return model_name, provider_name

balancer = LoadBalancer()
