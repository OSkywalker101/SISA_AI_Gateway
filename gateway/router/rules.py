from typing import Optional
from config import settings
from gateway.providers.base import ChatRequest

def detect_task_type(request: ChatRequest) -> str:
    """Analyze the prompt to detect the best matching task type."""
    prompt = request.messages[-1].content.lower() if request.messages else ""
    
    if "def " in prompt or "class " in prompt or "code" in prompt or "html" in prompt:
        return "code"
    
    if "summarize" in prompt or "tl;dr" in prompt or "short version" in prompt:
        return "summarize"
        
    if "logic" in prompt or "think step by step" in prompt or "explain" in prompt:
        return "reasoning"
        
    return "default"

def select_model(request: ChatRequest) -> str:
    """Run routing rules to pick the best model."""
    
    # Rule 1: Explicit Override from client requests
    if request.model and request.model != "auto":
        if request.model in settings.models:
            return request.model
    
    # Rule 2: Estimate cost threshold
    # Approximating tokens: 1 word ~ 1.3 tokens
    prompt = request.messages[-1].content if request.messages else ""
    estimated_prompt_tokens = len(prompt.split()) * 1.3
    
    task_type = detect_task_type(request)
    default_model = settings.task_type_routing.get(task_type, "gemini-1.5-flash")
    model_cfg = settings.models.get(default_model)
    
    if model_cfg:
        estimated_cost = (estimated_prompt_tokens / 1000.0) * model_cfg["cost_per_1k_tokens"]
        
        # Rule 3: Cost aware downgrade
        if estimated_cost > settings.cost_threshold_usd:
            # Downgrade to fastest/cheapest
            return "gemini-1.5-flash"

    return default_model
