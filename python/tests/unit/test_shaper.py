"""shape() contract tests - LLM output validation."""

import json

import pytest

from agentinterface.shaper import shape


class StubLLM:
    def __init__(self, payload: str):
        self.payload = payload

    async def generate(self, prompt: str) -> str:
        return self.payload


@pytest.mark.asyncio
async def test_shape_accepts_valid_component():
    llm = StubLLM('[{"type": "markdown", "data": {"content": "Hello"}}]')
    shaped = await shape("Hello", llm=llm)
    data = json.loads(shaped)
    assert data[0]["type"] == "markdown"


@pytest.mark.asyncio
async def test_shape_rejects_unknown_type():
    llm = StubLLM('[{"type": "nonexistent", "data": {}}]')
    with pytest.raises(ValueError):
        await shape("Hello", llm=llm)


@pytest.mark.asyncio
async def test_shape_enforces_required_fields():
    llm = StubLLM('[{"type": "embed", "data": {}}]')
    with pytest.raises(ValueError):
        await shape("Hello", llm=llm)


@pytest.mark.asyncio
async def test_shape_respects_whitelist():
    llm = StubLLM('[{"type": "card", "data": {}}]')
    with pytest.raises(ValueError):
        await shape("Hello", context={"components": ["markdown"]}, llm=llm)


@pytest.mark.asyncio
async def test_shape_without_llm():
    result = await shape("Hello world", llm=None)
    assert result == "Hello world"


@pytest.mark.asyncio
async def test_shape_rejects_invalid_json():
    llm = StubLLM("not json {")
    with pytest.raises(ValueError):
        await shape("Test", llm=llm)


@pytest.mark.asyncio
async def test_shape_rejects_non_array():
    llm = StubLLM('{"type": "markdown", "data": {"content": "test"}}')
    with pytest.raises(ValueError):
        await shape("Test", llm=llm)


@pytest.mark.asyncio
async def test_shape_nested_composition():
    nested = '[{"type": "card", "data": {"title": "Parent", "content": [{"type": "markdown", "data": {"content": "Child"}}]}}]'
    llm = StubLLM(nested)
    shaped = await shape("Test", llm=llm)
    data = json.loads(shaped)
    assert data[0]["data"]["content"][0]["type"] == "markdown"


@pytest.mark.asyncio
async def test_shape_horizontal_composition():
    composed = (
        '[[{"type": "card", "data": {"title": "L"}}, {"type": "card", "data": {"title": "R"}}]]'
    )
    llm = StubLLM(composed)
    shaped = await shape("Test", llm=llm)
    data = json.loads(shaped)
    assert isinstance(data[0], list)
    assert len(data[0]) == 2
