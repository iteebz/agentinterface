"""Protocol generation tests - component lists, composition patterns, defaults."""

from agentinterface import protocol


def test_protocol_generation():
    instructions = protocol(["card", "table"])

    assert "card" in instructions
    assert "table" in instructions
    assert "JSON" in instructions
    assert "array" in instructions.lower()


def test_protocol_subset_filtering():
    subset = ["card", "table"]
    instructions = protocol(subset)

    for component in subset:
        assert component in instructions

    excluded = ["timeline", "accordion", "tabs"]
    for component in excluded:
        assert component not in instructions


def test_protocol_explicit_list():
    instructions = protocol(["card", "table"])

    assert "card" in instructions
    assert "table" in instructions
    assert "timeline" not in instructions

    available = instructions.split("Composition patterns:")[0]
    lines = [ln for ln in available.split("\n") if ln.startswith("- ") and ":" in ln]
    listed = [ln.split(":")[0].replace("- ", "").strip() for ln in lines]
    assert set(listed) == {"card", "table"}


def test_protocol_empty_list():
    instructions = protocol([])
    assert "components:" in instructions.lower() or "markdown" in instructions


def test_protocol_single_component():
    instructions = protocol(["markdown"])
    assert "markdown" in instructions
    available = instructions.split("Composition patterns:")[0]
    assert "card" not in available


def test_protocol_composition_patterns():
    instructions = protocol(["card"])
    patterns = [
        "single:",
        "multiple:",
        "horizontal:",
        "mixed:",
    ]
    for pattern in patterns:
        assert pattern.lower() in instructions.lower()


def test_protocol_json_format():
    instructions = protocol(["card", "table"])
    assert "json" in instructions.lower()
    assert "return" in instructions.lower()
    assert "array" in instructions.lower()


def test_protocol_returns_string():
    result = protocol(["card"])
    assert isinstance(result, str)
    assert len(result) > 0


def test_protocol_none_components():
    instructions = protocol(None)
    assert isinstance(instructions, str)
    assert len(instructions) > 0
