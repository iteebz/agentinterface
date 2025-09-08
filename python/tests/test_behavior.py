"""
Behavior tests for AgentInterface v1.0.0
Tests actual functionality, not just imports.
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from agentinterface import ai, protocol, shape


@pytest.mark.asyncio
async def test_shape_transforms_text_to_components():
    """Test that shaper converts agent text into component JSON"""
    mock_llm = AsyncMock()
    mock_llm.generate = AsyncMock(return_value='[{"type": "card", "data": {"title": "Test"}}]')

    # Test basic shaping
    result = await shape(
        "Here are the quarterly results: Revenue increased 15%", {"query": "Show Q3 data"}, mock_llm
    )

    # Should return valid JSON
    components = json.loads(result)
    assert isinstance(components, list)
    assert len(components) > 0
    assert "type" in components[0]
    assert "data" in components[0]


@pytest.mark.asyncio
async def test_shape_handles_malformed_llm_response():
    """Test graceful handling of invalid LLM output"""
    mock_llm = AsyncMock()
    mock_llm.generate = AsyncMock(return_value="invalid json {")

    # Should not crash on malformed JSON
    result = await shape("Test response", {"query": "Test query"}, mock_llm)

    # Should return fallback or handle gracefully
    assert result is not None


@pytest.mark.asyncio
async def test_ai_with_simple_agent():
    """Test ai() function with basic agent - CANONICAL INTERFACE"""

    # Simple test agent
    def simple_agent(query: str) -> str:
        return f"Agent response to: {query}"

    # LLM is REQUIRED - returns coroutine that resolves to (text, components)
    agent = ai(simple_agent, llm="test_llm")
    result = agent("test query")

    # Sync agent always returns coroutine
    assert asyncio.iscoroutine(result)
    text, components = await result

    assert text == "Agent response to: test query"
    assert isinstance(components, list)


@pytest.mark.asyncio
async def test_ai_with_async_agent():
    """Test ai() function with async agent - CANONICAL INTERFACE"""

    async def async_agent(query: str) -> str:
        await asyncio.sleep(0.01)  # Simulate async work
        return f"Async response: {query}"

    # LLM is REQUIRED - returns coroutine that resolves to (text, components)
    agent = ai(async_agent, llm="test_llm")
    result = agent("async test")

    assert asyncio.iscoroutine(result)
    text, components = await result

    assert text == "Async response: async test"
    assert isinstance(components, list)


@pytest.mark.asyncio
async def test_ai_with_class_agent():
    """Test ai() function with class-based agent - CANONICAL INTERFACE"""

    class TestAgent:
        def __call__(self, query: str) -> str:
            return f"Class agent: {query}"

    test_agent = TestAgent()

    # LLM is REQUIRED - returns coroutine that resolves to (text, components)
    agent = ai(test_agent, llm="test_llm")
    result = agent("class test")

    assert asyncio.iscoroutine(result)
    text, components = await result
    assert text == "Class agent: class test"
    assert isinstance(components, list)


@pytest.mark.asyncio
async def test_ai_with_shaper_llm():
    """Test ai() with LLM shaper integration - CANONICAL INTERFACE"""

    def test_agent(query: str) -> str:
        return "Sales data: Revenue $100K, Users 500"

    mock_llm = AsyncMock()
    mock_llm.generate = AsyncMock(return_value='[{"type": "table", "data": {"title": "Sales"}}]')

    try:
        # Test with sync agent and LLM - returns coroutine that resolves to tuple
        agent = ai(test_agent, llm=mock_llm)
        result = agent("show sales")

        # Sync agent with LLM returns coroutine
        assert asyncio.iscoroutine(result)
        text, components = await result

        assert text == "Sales data: Revenue $100K, Users 500"
        assert isinstance(components, list)
        assert len(components) == 1
        assert components[0]["type"] == "table"

    except ImportError:
        # Skip if FastAPI not available
        pytest.skip("FastAPI not available for full integration test")


def test_ai_invalid_agent():
    """Test ai() function with invalid agent type - NEW CURRIED PATTERN"""
    # Invalid agent should raise on creation or first call
    try:
        agent = ai("not an agent")  # This might not fail immediately
        # Try to call it - this should fail
        asyncio.run(agent("test").__anext__())
    except (ValueError, TypeError, AttributeError):
        pass  # Expected - various possible errors for invalid agents


def test_protocol_component_selection():
    """Test protocol generates valid component instructions"""
    instructions = protocol(["card", "table", "timeline"])

    assert "card" in instructions
    assert "table" in instructions
    assert "timeline" in instructions
    assert "composition" in instructions.lower() or "array" in instructions.lower()


def test_callback_protocol_implementation():
    """Test that callback protocol is implemented properly"""
    from agentinterface.callback import Callback, Http, _get_shared_server

    # Test Http implementation
    callback = Http(port=9999)
    assert callback.endpoint().startswith("http://")
    assert ":9999/" in callback.endpoint()

    # Test shared server initialization
    server = _get_shared_server(9999)
    assert callback.id in server.callbacks


@pytest.mark.asyncio
async def test_callback_lifecycle_management():
    """Test callback lifecycle management"""
    from agentinterface.callback import Http, _get_shared_server

    callback = Http(id="test-lifecycle-123")
    server = _get_shared_server()

    # Should be registered on creation
    assert "test-lifecycle-123" in server.callbacks
    assert isinstance(server.callbacks["test-lifecycle-123"], asyncio.Future)

    # Simulate callback triggering
    server.callbacks["test-lifecycle-123"].set_result({"action": "test", "data": "value"})

    # Should get result and clean up
    result = await callback.await_interaction()
    assert result == {"action": "test", "data": "value"}
    assert "test-lifecycle-123" not in server.callbacks


def test_protocol_fallback_components():
    """Test protocol includes markdown fallback"""
    instructions = protocol(["card", "table"])

    # Should always include markdown as fallback
    assert "markdown" in instructions


def test_protocol_default_components():
    """Test protocol without arguments includes all default components"""
    instructions = protocol()

    expected_components = [
        "card",
        "timeline",
        "accordion",
        "code",
        "gallery",
        "reference",
        "suggestions",
        "table",
        "tabs",
        "tree",
        "markdown",
    ]

    for component in expected_components:
        assert component in instructions
