"""
Protocol generation tests - Schema-driven truth
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentinterface import protocol


def test_protocol_generation():
    """Protocol generates component instructions"""
    instructions = protocol(["card", "table"])

    assert "card" in instructions
    assert "table" in instructions
    assert "JSON" in instructions
    assert "array" in instructions.lower()


def test_protocol_subset_filtering():
    """Protocol respects component subsetting"""
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


def test_protocol_explicit_components_override():
    """Explicit component list overrides autodiscovery"""
    explicit_components = ["card", "suggestions"]
    instructions = protocol(explicit_components)

    # Extract only component list (before "Composition patterns:")
    available_section = instructions.split("Composition patterns:")[0]
    lines = available_section.split("\n")
    component_lines = [line for line in lines if line.startswith("- ") and ":" in line]
    listed_components = [line.split(":")[0].replace("- ", "").strip() for line in component_lines]

    assert set(listed_components) == set(explicit_components)


def test_protocol_explicit_components_used():
    """Protocol uses only explicitly provided components"""
    components = ["card", "markdown"]
    instructions = protocol(components)

    # Should contain explicit components
    assert "card" in instructions
    assert "markdown" in instructions

    # Should not contain others
    assert "timeline" not in instructions


def test_protocol_respects_explicit_list():
    """Protocol respects explicit component list"""
    instructions = protocol(["card", "table"])

    # Should only include explicitly requested components
    assert "card" in instructions
    assert "table" in instructions
    # Should not include other components when explicitly listed
    assert "timeline" not in instructions


if __name__ == "__main__":
    print("📋 Protocol Tests")
    test_protocol_generation()
    test_protocol_subset_filtering()
    test_protocol_explicit_components_override()
    test_protocol_explicit_components_used()
    test_protocol_respects_explicit_list()
    print("✅ All protocol tests passed")
