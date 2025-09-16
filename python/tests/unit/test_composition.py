"""
Composition pattern detection - Zero ceremony
"""

import json


def test_composition_detection():
    """Composition pattern detection"""
    # Single component
    single = [{"type": "card", "data": {}}]
    assert analyze_pattern(single) == "single"

    # Vertical stack
    vertical = [{"type": "card", "data": {}}, {"type": "card", "data": {}}]
    assert analyze_pattern(vertical) == "vertical"

    # Horizontal layout
    horizontal = [
        {"type": "card", "data": {}},
        [{"type": "card", "data": {}}, {"type": "card", "data": {}}],
    ]
    assert analyze_pattern(horizontal) == "horizontal"


def analyze_pattern(components):
    """Minimal pattern analysis"""
    if len(components) == 1:
        return "single"

    has_nested = any(isinstance(item, list) for item in components)
    return "horizontal" if has_nested else "vertical"


def test_json_validity():
    """All test compositions produce valid JSON"""
    test_compositions = [
        [{"type": "card", "data": {"title": "Test"}}],
        [
            {"type": "card", "data": {}},
            [{"type": "card", "data": {}}, {"type": "card", "data": {}}],
        ],
    ]

    for comp in test_compositions:
        json_str = json.dumps(comp)
        parsed = json.loads(json_str)
        assert parsed == comp


if __name__ == "__main__":
    print("🎯 Composition Tests")
    test_composition_detection()
    test_json_validity()
    print("✅ All composition tests passed")
