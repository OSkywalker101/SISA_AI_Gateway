import pytest
from gateway.router.rules import detect_task_type, select_model
from gateway.providers.base import ChatRequest, Message
from config import settings

def test_detect_task_type_code():
    req = ChatRequest(messages=[Message(role="user", content="def hello_world():")])
    assert detect_task_type(req) == "code"

def test_detect_task_type_summarize():
    req = ChatRequest(messages=[Message(role="user", content="Please summarize this article: ...")])
    assert detect_task_type(req) == "summarize"

def test_select_model_explicit_override():
    req = ChatRequest(model="anthropic-claude-stub", messages=[Message(role="user", content="Hi")])
    # Should route to the requested model explicitly
    assert select_model(req) == "anthropic-claude-stub"

def test_select_model_by_task_type():
    req = ChatRequest(messages=[Message(role="user", content="Write a python class for auth")])
    # Code tasks should go to gemini-1.5-pro (based on rules)
    assert select_model(req) == "gemini-1.5-pro"

def test_cost_threshold_routing():
    # very long prompt (cost > threshold)
    long_text = "word " * 15000 
    req = ChatRequest(messages=[Message(role="user", content=f"Fix this code: {long_text}")])
    # Should downgrade to gemini-flash because of cost
    assert select_model(req) == "gemini-1.5-flash"
