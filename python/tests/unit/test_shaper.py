"""
Shaper function tests - Pure transformation logic
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentinterface import shape


class MockLLM:
    """Deterministic LLM for canonical tests"""

    def __init__(self, response):
        self.response = response

    async def generate(self, prompt):
        return self.response


async def test_shape_transforms_text():
    """Shape converts text to component JSON"""
    llm = MockLLM('[{"type": "card", "data": {"title": "Test"}}]')
    result = await shape("test input", {"components": ["card"]}, llm)
    components = json.loads(result)

    assert isinstance(components, list)
    assert components[0]["type"] == "card"
    assert components[0]["data"]["title"] == "Test"


async def test_shape_handles_malformed():
    """Shape handles malformed LLM responses"""
    llm = MockLLM("invalid json {")

    # Should raise ValueError for invalid JSON
    try:
        await shape("test", {}, llm)
        raise AssertionError("Expected ValueError for malformed JSON")
    except ValueError:
        pass  # Expected behavior


async def test_shape_without_llm():
    """Shape without LLM returns input unchanged"""
    result = await shape("test input")
    assert result == "test input"


async def test_shape_empty_response():
    """Edge case validation"""
    llm = MockLLM("[]")  # Empty array
    result = await shape("test", {}, llm)
    components = json.loads(result)
    assert components == []


async def test_shape_unknown_component():
    """No components context"""
    llm = MockLLM('[{"type": "unknown", "data": {}}]')
    result = await shape("test", {}, llm)
    components = json.loads(result)
    assert components[0]["type"] == "unknown"  # Should pass through


if __name__ == "__main__":

    async def main():
        print("🎯 Shaper Tests")

        # Run async tests
        await test_shape_transforms_text()
        await test_shape_handles_malformed()
        await test_shape_without_llm()
        await test_shape_empty_response()
        await test_shape_unknown_component()

        print("✅ All shaper tests passed")

    asyncio.run(main())
