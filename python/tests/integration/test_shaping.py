"""Shaper integration - registry loading, validation, edge cases."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from agentinterface.shaper import _load_registry, _validate_component_tree, shape


class StubLLM:
    def __init__(self, response: str):
        self.response = response

    async def generate(self, prompt: str) -> str:
        return self.response


@pytest.mark.asyncio
async def test_shape_validates_component_contract():
    """shape() validates that LLM returns valid component array."""
    llm = StubLLM('[{"type": "markdown", "data": {"content": "text"}}]')
    result = await shape("Input", llm=llm)
    data = json.loads(result)
    assert isinstance(data, list)
    assert data[0]["type"] == "markdown"


@pytest.mark.asyncio
async def test_shape_rejects_non_array_output():
    """LLM returning object (not array) raises ValueError."""
    llm = StubLLM('{"type": "markdown"}')
    with pytest.raises(ValueError, match="must return array"):
        await shape("Input", llm=llm)


@pytest.mark.asyncio
async def test_shape_rejects_invalid_json():
    """Invalid JSON from LLM raises immediately."""
    llm = StubLLM("not json {")
    with pytest.raises(ValueError, match="Invalid JSON"):
        await shape("Input", llm=llm)


@pytest.mark.asyncio
async def test_shape_strips_markdown_fences():
    """LLM output wrapped in code fences is unwrapped."""
    llm = StubLLM('```json\n[{"type": "markdown", "data": {"content": "x"}}]\n```')
    result = await shape("Input", llm=llm)
    data = json.loads(result)
    assert len(data) == 1


@pytest.mark.asyncio
async def test_shape_respects_allowed_components():
    """Components not in whitelist are rejected."""
    llm = StubLLM('[{"type": "card", "data": {}}]')
    with pytest.raises(ValueError, match="not permitted"):
        await shape("Input", context={"components": ["markdown"]}, llm=llm)


@pytest.mark.asyncio
async def test_shape_enforces_required_fields():
    """Components missing required schema fields raise."""
    llm = StubLLM('[{"type": "embed", "data": {}}]')
    with pytest.raises(ValueError, match="missing required"):
        await shape("Input", llm=llm)


@pytest.mark.asyncio
async def test_shape_handles_nested_components():
    """Nested component structures validate recursively."""
    nested = '[{"type": "card", "data": {"title": "Parent", "content": [{"type": "markdown", "data": {"content": "Child"}}]}}]'
    llm = StubLLM(nested)
    result = await shape("Input", llm=llm)
    data = json.loads(result)
    assert data[0]["type"] == "card"


@pytest.mark.asyncio
async def test_shape_handles_array_composition():
    """Array-of-arrays composition (horizontal layout) validates."""
    composed = (
        '[[{"type": "card", "data": {"title": "L"}}, {"type": "card", "data": {"title": "R"}}]]'
    )
    llm = StubLLM(composed)
    result = await shape("Input", llm=llm)
    data = json.loads(result)
    assert isinstance(data[0], list)
    assert len(data[0]) == 2


@pytest.mark.asyncio
async def test_load_registry_searches_upward():
    """Registry search looks in cwd, then parents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        registry_file = tmppath / "ai.json"
        registry_file.write_text(json.dumps({"components": {"card": {"schema": {}}}}))

        with patch("pathlib.Path.cwd", return_value=tmppath / "subdir"):
            registry = _load_registry()
            assert "card" in registry


@pytest.mark.asyncio
async def test_load_registry_missing_returns_empty():
    """No ai.json found returns empty dict."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
            registry = _load_registry()
            assert registry == {}


@pytest.mark.asyncio
async def test_load_registry_invalid_json_returns_empty():
    """Malformed ai.json returns empty dict."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        registry_file = tmppath / "ai.json"
        registry_file.write_text("not json {")

        with patch("pathlib.Path.cwd", return_value=tmppath):
            registry = _load_registry()
            assert registry == {}


@pytest.mark.asyncio
async def test_load_registry_missing_components_key():
    """ai.json without 'components' key returns empty."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        registry_file = tmppath / "ai.json"
        registry_file.write_text(json.dumps({"other_key": {}}))

        with patch("pathlib.Path.cwd", return_value=tmppath):
            registry = _load_registry()
            assert registry == {}


def test_validate_component_tree_accepts_markdown():
    """Valid markdown component passes validation."""
    data = [{"type": "markdown", "data": {"content": "text"}}]
    _validate_component_tree(data)


def test_validate_component_tree_rejects_non_array():
    """Top-level must be array."""
    with pytest.raises(ValueError, match="must be a JSON array"):
        _validate_component_tree({"type": "markdown"})


def test_validate_component_tree_rejects_missing_type():
    """Every component must have 'type' string."""
    with pytest.raises(ValueError, match="missing string 'type'"):
        _validate_component_tree([{"data": {}}])


def test_validate_component_tree_rejects_empty_type():
    """Empty string type is invalid."""
    with pytest.raises(ValueError, match="missing string 'type'"):
        _validate_component_tree([{"type": "", "data": {}}])


def test_validate_component_tree_rejects_non_string_type():
    """Type must be string, not number."""
    with pytest.raises(ValueError, match="missing string 'type'"):
        _validate_component_tree([{"type": 123, "data": {}}])


def test_validate_component_tree_rejects_non_dict_element():
    """List elements must be dicts (for composition), not arrays of scalars."""
    with pytest.raises(ValueError, match="must be an object"):
        _validate_component_tree([["string", "array"]])


def test_validate_component_tree_data_must_be_dict():
    """Data field must be object, not array."""
    with pytest.raises(ValueError, match="data must be an object"):
        _validate_component_tree([{"type": "markdown", "data": ["invalid"]}])


def test_validate_component_tree_handles_null_data():
    """Null data is converted to empty dict (but may fail schema validation)."""
    data = [{"type": "markdown", "data": None}]
    with pytest.raises(ValueError, match="missing required"):
        _validate_component_tree(data)


def test_validate_component_tree_composition_valid():
    """Mixed single components and arrays (composition) is valid."""
    data = [
        {"type": "markdown", "data": {"content": "text"}},
        [
            {"type": "card", "data": {"title": "A"}},
            {"type": "card", "data": {"title": "B"}},
        ],
    ]
    _validate_component_tree(data)


def test_validate_component_tree_allowed_enforcement():
    """Only whitelisted component types allowed."""
    data = [{"type": "card", "data": {"title": "Title"}}]
    with pytest.raises(ValueError, match="not permitted"):
        _validate_component_tree(data, allowed=["markdown"])


def test_validate_component_tree_allowed_permits():
    """Whitelisted types pass."""
    data = [{"type": "card", "data": {"title": "Title"}}]
    _validate_component_tree(data, allowed=["card", "table"])
