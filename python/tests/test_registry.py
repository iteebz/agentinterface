"""Test registry loading behavior."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from agentinterface.ai import protocol


def test_protocol_loads_from_registry():
    """Protocol should load components from ai.json registry."""
    registry_data = {
        "components": {
            "custom1": {"description": "Custom component 1"},
            "custom2": {"description": "Custom component 2"},
            "markdown": {"description": "Fallback component"},
        }
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        registry_path = Path(temp_dir) / "ai.json"
        registry_path.write_text(json.dumps(registry_data))

        with patch("agentinterface.ai.Path.cwd", return_value=Path(temp_dir)):
            result = protocol()

            # Should include components from registry
            assert "custom1" in result
            assert "custom2" in result
            assert "markdown" in result  # Always included


def test_protocol_malformed_registry_fallback():
    """Malformed ai.json should fall back to built-in components."""
    with tempfile.TemporaryDirectory() as temp_dir:
        registry_path = Path(temp_dir) / "ai.json"
        registry_path.write_text("invalid json content")

        with patch("agentinterface.ai.Path.cwd", return_value=Path(temp_dir)):
            result = protocol()

            # Should fall back to built-ins
            assert "card" in result
            assert "table" in result
            assert "markdown" in result


def test_protocol_empty_registry_fallback():
    """Empty registry should fall back to built-in components."""
    registry_data = {"components": {}}

    with tempfile.TemporaryDirectory() as temp_dir:
        registry_path = Path(temp_dir) / "ai.json"
        registry_path.write_text(json.dumps(registry_data))

        with patch("agentinterface.ai.Path.cwd", return_value=Path(temp_dir)):
            result = protocol()

            # Should fall back to built-ins
            assert "card" in result
            assert "table" in result
            assert "markdown" in result


def test_protocol_missing_registry_fallback():
    """Missing ai.json should fall back to built-in components."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # No ai.json file created

        with patch("agentinterface.ai.Path.cwd", return_value=Path(temp_dir)):
            result = protocol()

            # Should fall back to built-ins
            assert "card" in result
            assert "table" in result
            assert "markdown" in result


def test_protocol_explicit_components_override():
    """Explicit component list should override registry."""
    registry_data = {
        "components": {
            "custom1": {"description": "Custom component 1"},
            "custom2": {"description": "Custom component 2"},
        }
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        registry_path = Path(temp_dir) / "ai.json"
        registry_path.write_text(json.dumps(registry_data))

        with patch("agentinterface.ai.Path.cwd", return_value=Path(temp_dir)):
            result = protocol(["table", "timeline"])

            # Should use explicit list, not registry
            assert "table" in result
            assert "timeline" in result
            assert "markdown" in result  # Always added
            assert "custom1" not in result
            assert "custom2" not in result


def test_protocol_markdown_always_included():
    """Markdown should always be included even with custom components."""
    result = protocol(["card", "table"])

    assert "card" in result
    assert "table" in result
    assert "markdown" in result  # Always included

    # Test when markdown already in list
    result2 = protocol(["card", "markdown", "table"])

    # Check that components line only lists markdown once
    components_line = [
        line for line in result2.split("\n") if line.startswith("Available components:")
    ][0]
    markdown_count_in_list = components_line.count("markdown")
    assert markdown_count_in_list == 1
