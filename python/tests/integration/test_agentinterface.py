"""ai() wrapper integration tests"""

import asyncio
from unittest.mock import AsyncMock

import pytest

from agentinterface import ai


def mock_llm():
    """Create mock LLM that returns markdown fallback."""
    llm = AsyncMock()
    llm.generate = AsyncMock(return_value='[{"type": "markdown", "data": {"content": "fallback"}}]')
    return llm


@pytest.mark.asyncio
async def test_ai_with_simple_agent():
    def simple_agent(query: str) -> str:
        return f"Agent response to: {query}"

    enhanced = ai(simple_agent, llm=mock_llm())
    result = enhanced("test query")

    assert asyncio.iscoroutine(result)
    text, components = await result
    assert text == "Agent response to: test query"
    assert isinstance(components, list)


@pytest.mark.asyncio
async def test_ai_with_async_agent():
    async def async_agent(query: str) -> str:
        await asyncio.sleep(0.01)
        return f"Async response: {query}"

    enhanced = ai(async_agent, llm=mock_llm())
    result = enhanced("async test")

    assert asyncio.iscoroutine(result)
    text, components = await result

    assert text == "Async response: async test"
    assert isinstance(components, list)


@pytest.mark.asyncio
async def test_ai_with_class_agent():
    class TestAgent:
        def __call__(self, query: str) -> str:
            return f"Class agent: {query}"

    enhanced = ai(TestAgent(), llm=mock_llm())
    result = enhanced("class test")

    assert asyncio.iscoroutine(result)
    text, components = await result
    assert text == "Class agent: class test"
    assert isinstance(components, list)


@pytest.mark.asyncio
async def test_ai_with_shaper_llm():
    def test_agent(query: str) -> str:
        return "Sales data: Revenue $100K, Users 500"

    llm = AsyncMock()
    llm.generate = AsyncMock(
        return_value='[{"type": "card", "data": {"title": "Sales", "content": "Revenue $100K"}}]'
    )

    enhanced = ai(test_agent, llm=llm)
    result = enhanced("show sales")
    assert asyncio.iscoroutine(result)
    text, components = await result

    assert text == "Sales data: Revenue $100K, Users 500"
    assert isinstance(components, list)
    assert len(components) == 1
    assert components[0]["type"] == "card"


def test_ai_invalid_agent():
    with pytest.raises((ValueError, TypeError, AttributeError)):
        enhanced = ai("not an agent", llm=mock_llm())
        asyncio.run(enhanced("test"))
