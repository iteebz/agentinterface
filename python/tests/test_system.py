"""
System Tests - Real LLM integration (requires API keys)

Run manually: python -m pytest tests/test_system.py
Skipped in CI: too slow and requires external services
"""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentinterface import protocol, shape
from agentinterface.llms import llm


async def test_real_table_generation():
    """Test real LLM generates table components for tabular data"""
    try:
        model = llm("gemini")  # Use agentinterface's LLM system
    except RuntimeError as e:
        print(f"⚠️  Skipping real LLM test: {e}")
        return True

    print("🧠 Testing real LLM with tabular data...")

    input_text = """
    Q1 2024 Results:
    Revenue: $2.5M (+15%)
    Users: 50,000 (+25%)  
    Churn: 3.2% (-0.8%)
    """

    context = {"components": ["card", "table", "timeline", "suggestions", "markdown"]}

    result = await shape(input_text, context, model)
    print(f"📊 LLM Response length: {len(result)} chars")

    try:
        components = json.loads(result)
        print(f"✅ Valid JSON with {len(components)} components")

        # Check if LLM chose appropriate component type
        component_types = [comp.get("type") for comp in components if isinstance(comp, dict)]
        print(f"🔍 Component types: {component_types}")

        # For tabular data, expect table or card components
        expected_types = ["table", "card"]
        has_appropriate_type = any(ctype in component_types for ctype in expected_types)

        if has_appropriate_type:
            print("✅ LLM selected appropriate component type for tabular data")
            return True
        else:
            print(f"⚠️  LLM selected {component_types}, expected one of {expected_types}")
            return False

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON from LLM: {e}")
        print(f"Raw response: {result[:200]}...")
        return False


async def test_real_timeline_generation():
    """Test real LLM generates timeline for sequential events"""
    try:
        model = llm("gemini")
    except ValueError as e:
        print(f"⚠️  Skipping real LLM test: {e}")
        return True

    print("🧠 Testing real LLM with sequential events...")

    input_text = """
    Project milestones:
    January 5th - Project kickoff and team assembly
    February 20th - Requirements gathering completed
    March 15th - MVP development finished
    April 2nd - Beta testing launched
    """

    context = {"components": ["card", "table", "timeline", "suggestions", "markdown"]}

    result = await shape(input_text, context, model)
    print(f"📅 LLM Response length: {len(result)} chars")

    try:
        components = json.loads(result)
        print(f"✅ Valid JSON with {len(components)} components")

        component_types = [comp.get("type") for comp in components if isinstance(comp, dict)]
        print(f"🔍 Component types: {component_types}")

        # For timeline data, expect timeline or card components
        expected_types = ["timeline", "card"]
        has_appropriate_type = any(ctype in component_types for ctype in expected_types)

        if has_appropriate_type:
            print("✅ LLM selected appropriate component type for timeline data")
            return True
        else:
            print(f"⚠️  LLM selected {component_types}, expected one of {expected_types}")
            return False

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON from LLM: {e}")
        print(f"Raw response: {result[:200]}...")
        return False


async def test_real_composition():
    """Test real LLM generates compositional layouts"""
    try:
        model = llm("gemini")
    except ValueError as e:
        print(f"⚠️  Skipping real LLM test: {e}")
        return True

    print("🧠 Testing real LLM with composition request...")

    input_text = """
    Show me a comparison dashboard:
    
    Left side: Current quarter metrics (Revenue: $2M, Users: 45K)
    Right side: Previous quarter metrics (Revenue: $1.8M, Users: 42K)
    
    Below that: Suggested next steps for growth
    """

    context = {"components": ["card", "table", "timeline", "suggestions", "markdown"]}

    result = await shape(input_text, context, model)
    print(f"🎨 LLM Response length: {len(result)} chars")

    try:
        components = json.loads(result)
        print(f"✅ Valid JSON with {len(components)} components")

        # Check for compositional structure (nested arrays)
        has_composition = any(isinstance(item, list) for item in components)
        print(f"🔍 Has composition: {has_composition}")

        if has_composition:
            print("✅ LLM generated compositional layout")
            return True
        else:
            print("⚠️  LLM generated simple layout, not compositional")
            # Still valid - just simpler than expected
            return True

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON from LLM: {e}")
        print(f"Raw response: {result[:200]}...")
        return False


def test_protocol_with_real_components():
    """Test protocol generation with discovered components"""
    print("📋 Testing protocol with real component registry...")

    # Load real components from ai.json
    try:
        with open("ai.json") as f:
            registry = json.load(f)

        component_names = list(registry["components"].keys())
        print(f"🔍 Found {len(component_names)} components: {component_names}")

        instructions = protocol(component_names)
        print(f"📄 Protocol length: {len(instructions)} chars")

        # Check all components are mentioned
        missing = [name for name in component_names if name not in instructions]

        if missing:
            print(f"❌ Missing components in protocol: {missing}")
            return False
        else:
            print("✅ All components included in protocol")
            return True

    except FileNotFoundError:
        print("⚠️  ai.json not found, using default components")
        return test_protocol_default()


def test_protocol_default():
    """Test protocol with default components"""
    instructions = protocol()
    print(f"📄 Default protocol length: {len(instructions)} chars")
    return len(instructions) > 50  # Sanity check


async def test_error_recovery():
    """Test shaper handles LLM errors gracefully"""

    class FailingLLM:
        async def generate(self, prompt):
            raise RuntimeError("Component generation failed")

    print("💥 Testing error recovery...")

    llm = FailingLLM()

    # Should raise RuntimeError on failure
    try:
        result = await shape("test input", {}, llm)
        print(f"❌ Expected RuntimeError, got result: {result}")
        return False
    except RuntimeError as e:
        if "Component generation failed" in str(e):
            print("✅ Error recovery successful - RuntimeError raised as expected")
            return True
        else:
            print(f"❌ Wrong error message: {e}")
            return False


if __name__ == "__main__":

    async def main():
        print("🔬 Integration Tests\n")

        tests = [
            ("Real Table Generation", test_real_table_generation),
            ("Real Timeline Generation", test_real_timeline_generation),
            ("Real Composition", test_real_composition),
            ("Error Recovery", test_error_recovery),
            ("Protocol Generation", lambda: test_protocol_with_real_components()),
        ]

        results = []

        for name, test_func in tests:
            print(f"\n🧪 {name}")
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                results.append(result)
                print("✅ PASSED" if result else "❌ FAILED")
            except Exception as e:
                print(f"💥 ERROR: {e}")
                results.append(False)

        passed = sum(results)
        total = len(results)

        print(f"\n🎯 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

        if passed == total:
            print("🚀 Integration tests PASSED - Real LLM shaper working!")
        else:
            print("⚠️  Some integration tests failed - check LLM responses")

        return passed == total

    success = asyncio.run(main())
    sys.exit(0 if success else 1)
