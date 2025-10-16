"""ai() wrapper integration tests - contract validation only."""

import asyncio
import json
from unittest.mock import AsyncMock

import pytest

from agentinterface import ai
from agentinterface.callback import Http


class StubLLM:
    def __init__(self, response: str):
        self.response = response

    async def generate(self, prompt: str) -> str:
        return self.response


@pytest.mark.asyncio
async def test_sync_agent_returns_text_components_tuple():
    """Sync agent wrapped by ai() returns Awaitable[tuple[str, list]]."""

    def agent(q: str) -> str:
        return "Result"

    wrapped = ai(agent, llm=StubLLM('[{"type": "markdown", "data": {"content": "x"}}]'))
    result = wrapped("query")

    assert asyncio.iscoroutine(result)
    text, components = await result
    assert isinstance(text, str)
    assert isinstance(components, list)
    assert len(components) > 0


@pytest.mark.asyncio
async def test_async_agent_returns_text_components_tuple():
    """Async agent wrapped by ai() returns Awaitable[tuple[str, list]]."""

    async def agent(q: str) -> str:
        return "Async result"

    wrapped = ai(agent, llm=StubLLM('[{"type": "markdown", "data": {"content": "x"}}]'))
    result = wrapped("query")

    assert asyncio.iscoroutine(result)
    text, components = await result
    assert text == "Async result"
    assert isinstance(components, list)


@pytest.mark.asyncio
async def test_streaming_agent_yields_events_then_components():
    """Streaming agent yields events, ai() collects text, appends components."""

    async def stream_agent(q: str):
        yield "Event 1: "
        yield "Event 2"

    wrapped = ai(
        stream_agent, llm=StubLLM('[{"type": "markdown", "data": {"content": "collected"}}]')
    )
    result = wrapped("query")

    events = []
    async for evt in result:
        events.append(evt)

    assert len(events) >= 3
    component_events = [e for e in events if isinstance(e, dict) and e.get("type") == "component"]
    assert len(component_events) > 0


@pytest.mark.asyncio
async def test_shaper_llm_generates_valid_components():
    """LLM shaper generates component JSON from agent response."""

    def agent(q: str) -> str:
        return "Revenue: $100K"

    llm = StubLLM('[{"type": "card", "data": {"title": "Revenue", "value": "$100K"}}]')
    wrapped = ai(agent, llm=llm)
    text, components = await wrapped("query")

    assert text == "Revenue: $100K"
    assert components[0]["type"] == "card"
    assert components[0]["data"]["title"] == "Revenue"


@pytest.mark.asyncio
async def test_shaper_fallback_on_llm_failure():
    """If LLM fails, ai() falls back to markdown."""

    def agent(q: str) -> str:
        return "Text content"

    llm = StubLLM("not valid json {")
    wrapped = ai(agent, llm=llm)
    text, components = await wrapped("query")

    assert text == "Text content"
    assert components[0]["type"] == "markdown"
    assert components[0]["data"]["content"] == "Text content"


@pytest.mark.asyncio
async def test_ai_respects_component_whitelist():
    """ai() passes allowed components to shaper."""

    def agent(q: str) -> str:
        return "Data"

    llm = StubLLM('[{"type": "card", "data": {"title": "Title"}}]')
    wrapped = ai(agent, llm=llm, components=["card", "table"])
    text, components = await wrapped("query")

    assert components[0]["type"] == "card"


@pytest.mark.asyncio
async def test_streaming_empty_events_handled():
    """Streaming agent with empty events doesn't crash."""

    async def stream_agent(q: str):
        yield ""
        yield None
        yield "Some text"

    wrapped = ai(stream_agent, llm=StubLLM('[{"type": "markdown", "data": {"content": "x"}}]'))
    result = wrapped("query")

    events = []
    async for evt in result:
        events.append(evt)

    assert len(events) > 0


@pytest.mark.asyncio
async def test_streaming_with_callback_integration():
    """Streaming agent with callback yields component with endpoint."""

    async def stream_agent(q: str):
        yield "Content"

    callback = Http(id="test-cb")
    wrapped = ai(
        stream_agent,
        llm=StubLLM('[{"type": "markdown", "data": {"content": "x"}}]'),
        callback=callback,
    )
    result = wrapped("query")

    component_event = None
    async for evt in result:
        if isinstance(evt, dict) and evt.get("type") == "component":
            component_event = evt
            break

    assert component_event is not None
    assert "callback_url" in component_event["data"]
    assert callback.id in component_event["data"]["callback_url"]


@pytest.mark.asyncio
async def test_ai_extract_text_from_dict_events():
    """ai() extracts text from dict events with various keys."""

    async def stream_agent(q: str):
        yield {"content": "From content key"}
        yield {"text": "From text key"}
        yield {"message": "From message key"}

    wrapped = ai(
        stream_agent, llm=StubLLM('[{"type": "markdown", "data": {"content": "extracted"}}]')
    )
    result = wrapped("query")

    event_count = 0
    async for _ in result:
        event_count += 1

    assert event_count >= 4


@pytest.mark.asyncio
async def test_rotator_integration_with_rate_limit():
    """ai() with rotation handles rate limit signal."""
    call_count = 0

    async def failing_llm(prompt: str) -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("rate limit exceeded")
        return '[{"type": "markdown", "data": {"content": "recovered"}}]'

    llm = AsyncMock()
    llm.generate = failing_llm

    def agent(q: str) -> str:
        return "Query"

    wrapped = ai(agent, llm=llm)
    text, components = await wrapped("test")

    assert text == "Query"
    assert isinstance(components, list)


@pytest.mark.asyncio
async def test_agent_with_multiple_args():
    """ai() preserves agent args through wrapper."""

    def agent(query: str, context: str) -> str:
        return f"{query}:{context}"

    wrapped = ai(agent, llm=StubLLM('[{"type": "markdown", "data": {"content": "x"}}]'))
    text, components = await wrapped("Q1", "ctx")

    assert text == "Q1:ctx"
    assert isinstance(components, list)


@pytest.mark.asyncio
async def test_streaming_collects_all_text_before_components():
    """Streaming agent collects all yielded text, then generates components once."""

    async def stream_agent(q: str):
        for i in range(5):
            yield f"Chunk {i} "

    llm = AsyncMock()
    llm.generate = AsyncMock(return_value='[{"type": "markdown", "data": {"content": "x"}}]')

    wrapped = ai(stream_agent, llm=llm)
    events = []
    async for evt in wrapped("query"):
        events.append(evt)

    assert llm.generate.call_count == 1
    call_args = llm.generate.call_args[0][0]
    assert "Chunk 0" in call_args
    assert "Chunk 4" in call_args


@pytest.mark.asyncio
async def test_component_validation_fallback_on_error():
    """Invalid component from LLM falls back to markdown (doesn't raise)."""

    def agent(q: str) -> str:
        return "Original text"

    llm = StubLLM('[{"type": "nonexistent", "data": {}}]')
    wrapped = ai(agent, llm=llm)
    text, components = await wrapped("query")

    assert text == "Original text"
    assert components[0]["type"] == "markdown"
    assert components[0]["data"]["content"] == "Original text"


@pytest.mark.asyncio
async def test_ai_timeout_with_callback_logs_warning():
    """ai() with callback timeout logs warning and continues."""

    async def stream_agent(q: str):
        yield "Content"

    callback = Http(id="timeout-test")
    wrapped = ai(
        stream_agent,
        llm=StubLLM('[{"type": "markdown", "data": {"content": "x"}}]'),
        callback=callback,
        timeout=0.001,
    )
    result = wrapped("query")

    events = []
    async for evt in result:
        events.append(evt)

    assert len(events) > 0
