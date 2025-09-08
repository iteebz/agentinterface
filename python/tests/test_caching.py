"""Test component caching behavior."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from agentinterface.ai import _component_cache, _generate_components


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache between tests."""
    _component_cache.clear()
    yield
    _component_cache.clear()


@pytest.mark.asyncio
async def test_component_cache_hit():
    """Same text + components should use cache."""
    with patch("agentinterface.ai.shape") as mock_shape:
        mock_shape.return_value = '[{"type": "card", "data": {"title": "Test"}}]'

        agent_args = ["test query"]
        components = ["card", "markdown"]
        text = "Test content"
        mock_llm = AsyncMock()

        # First call - should call shape
        result1 = await _generate_components(text, agent_args, components, mock_llm)

        # Second call - should use cache
        result2 = await _generate_components(text, agent_args, components, mock_llm)

        # Shape should only be called once
        mock_shape.assert_called_once()

        # Results should be identical
        assert result1 == result2
        assert result1 == [{"type": "card", "data": {"title": "Test"}}]


@pytest.mark.asyncio
async def test_component_cache_miss():
    """Different text should generate new components."""
    with patch("agentinterface.ai.shape") as mock_shape:
        mock_shape.side_effect = [
            '[{"type": "card", "data": {"title": "First"}}]',
            '[{"type": "table", "data": {"rows": []}}]',
        ]

        agent_args = ["test query"]
        components = ["card", "markdown"]
        mock_llm = AsyncMock()

        # Different text should miss cache
        result1 = await _generate_components("First content", agent_args, components, mock_llm)
        result2 = await _generate_components("Second content", agent_args, components, mock_llm)

        # Shape should be called twice
        assert mock_shape.call_count == 2

        # Results should be different
        assert result1 != result2
        assert result1 == [{"type": "card", "data": {"title": "First"}}]
        assert result2 == [{"type": "table", "data": {"rows": []}}]


@pytest.mark.asyncio
async def test_component_cache_different_components():
    """Different component lists should miss cache."""
    with patch("agentinterface.ai.shape") as mock_shape:
        mock_shape.side_effect = [
            '[{"type": "card", "data": {"title": "Test"}}]',
            '[{"type": "table", "data": {"rows": []}}]',
        ]

        agent_args = ["test query"]
        text = "Same content"
        mock_llm = AsyncMock()

        # Different component lists should miss cache
        result1 = await _generate_components(text, agent_args, ["card"], mock_llm)
        result2 = await _generate_components(text, agent_args, ["table"], mock_llm)

        # Shape should be called twice
        assert mock_shape.call_count == 2
        assert result1 != result2


@pytest.mark.asyncio
async def test_cache_fallback_behavior():
    """Fallback components should also be cached."""
    with patch("agentinterface.ai.shape") as mock_shape:
        mock_shape.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)

        agent_args = ["test query"]
        components = ["card", "markdown"]
        text = "Test content"
        mock_llm = AsyncMock()

        # First call - should fallback and cache
        result1 = await _generate_components(text, agent_args, components, mock_llm)

        # Second call - should use cached fallback
        result2 = await _generate_components(text, agent_args, components, mock_llm)

        # Shape should only be called once
        mock_shape.assert_called_once()

        # Both should be markdown fallback
        expected = [{"type": "markdown", "data": {"content": "Test content"}}]
        assert result1 == expected
        assert result2 == expected
