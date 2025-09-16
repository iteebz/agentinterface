"""Validation tests for component shaping."""

import json
import pytest

from agentinterface.shaper import shape


class StubLLM:
    def __init__(self, payload: str):
        self.payload = payload

    async def generate(self, prompt: str) -> str:  # pragma: no cover - simple stub
        return self.payload


@pytest.mark.asyncio
async def test_shape_accepts_known_component():
    llm = StubLLM('[{"type": "markdown", "data": {"content": "Hello"}}]')
    shaped = await shape("Hello", llm=llm)
    data = json.loads(shaped)
    assert data[0]["type"] == "markdown"


@pytest.mark.asyncio
async def test_shape_rejects_unknown_component_type():
    llm = StubLLM('[{"type": "totally_fake", "data": {}}]')
    with pytest.raises(ValueError):
        await shape("Hello", llm=llm)


@pytest.mark.asyncio
async def test_shape_enforces_required_fields():
    llm = StubLLM('[{"type": "embed", "data": {}}]')
    with pytest.raises(ValueError):
        await shape("Hello", llm=llm)


@pytest.mark.asyncio
async def test_shape_respects_allowed_component_list():
    llm = StubLLM('[{"type": "card", "data": {}}]')
    with pytest.raises(ValueError):
        await shape("Hello", context={"components": ["markdown"]}, llm=llm)
