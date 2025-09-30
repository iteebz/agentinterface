"""shape() integration tests"""

import json
from unittest.mock import AsyncMock

import pytest

from agentinterface import shape


@pytest.mark.asyncio
async def test_shape_transforms_text():
    mock_llm = AsyncMock()
    mock_llm.generate = AsyncMock(return_value='[{"type": "card", "data": {"title": "Test"}}]')

    result = await shape(
        "Here are the quarterly results: Revenue increased 15%", {"query": "Show Q3 data"}, mock_llm
    )

    components = json.loads(result)
    assert isinstance(components, list)
    assert len(components) > 0
    assert "type" in components[0]
    assert "data" in components[0]


@pytest.mark.asyncio
async def test_shape_handles_malformed_json():
    mock_llm = AsyncMock()
    mock_llm.generate = AsyncMock(return_value="invalid json {")

    with pytest.raises(ValueError, match="Invalid JSON from LLM"):
        await shape("Test response", {"query": "Test query"}, mock_llm)
