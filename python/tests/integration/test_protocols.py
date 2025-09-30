"""protocol() integration tests"""

import json
from pathlib import Path

from agentinterface import protocol


def test_protocol_includes_composition():
    instructions = protocol(["card", "table", "timeline"])

    assert "card" in instructions
    assert "table" in instructions
    assert "timeline" in instructions
    assert "composition" in instructions.lower() or "array" in instructions.lower()


def test_protocol_fallback_components():
    instructions = protocol(["card", "table"])

    assert "card" in instructions
    assert "table" in instructions
    assert "timeline" not in instructions


def test_protocol_default_components():
    instructions = protocol()

    assert "markdown" in instructions

    registry_path = Path.cwd() / "ai.json"
    if registry_path.exists():
        registry = json.loads(registry_path.read_text())
        expected_components = list(registry.get("components", {}).keys())
        for component in expected_components:
            assert component in instructions
