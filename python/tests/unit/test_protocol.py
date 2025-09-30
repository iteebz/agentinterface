"""
Protocol generation tests - Schema-driven truth
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentinterface import protocol


def test_protocol_generation():
    instructions = protocol(["card", "table"])

    assert "card" in instructions
    assert "table" in instructions
    assert "JSON" in instructions
    assert "array" in instructions.lower()


def test_protocol_subset_filtering():
    # Test with specific components
    subset = ["card", "table"]
    instructions = protocol(subset)

    # Should only mention subset components
    for component in subset:
        assert component in instructions

    # Should not mention other components
    excluded = ["timeline", "accordion", "tabs"]
    for component in excluded:
        assert component not in instructions


def test_protocol_explicit_list():
    instructions = protocol(["card", "table"])

    assert "card" in instructions
    assert "table" in instructions
    assert "timeline" not in instructions

    # Verify list section contains only requested components
    available = instructions.split("Composition patterns:")[0]
    lines = [ln for ln in available.split("\n") if ln.startswith("- ") and ":" in ln]
    listed = [ln.split(":")[0].replace("- ", "").strip() for ln in lines]
    assert set(listed) == {"card", "table"}


if __name__ == "__main__":
    print("📋 Protocol Tests")
    test_protocol_generation()
    test_protocol_subset_filtering()
    test_protocol_explicit_list()
    print("✅ All protocol tests passed")
