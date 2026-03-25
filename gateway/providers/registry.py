from gateway.providers.base import BaseProvider
from gateway.providers.gemini_provider import GeminiProvider
from gateway.providers.openai_provider import OpenAIStubProvider
from gateway.providers.anthropic_provider import AnthropicStubProvider

# Register all initialized providers
providers_instance_registry = {
    "gemini": GeminiProvider(),
    "openai": OpenAIStubProvider(),
    "anthropic": AnthropicStubProvider()
}

def get_provider_instance(provider_name: str) -> BaseProvider:
    if provider_name in providers_instance_registry:
        return providers_instance_registry[provider_name]
    raise ValueError(f"Provider {provider_name} not found in registry")
