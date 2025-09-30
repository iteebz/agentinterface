"""LLM factory unit tests - Pure logic, no external calls"""

import pytest

from agentinterface.llms import LLM, create_llm


class MockLLM(LLM):
    """Mock LLM for testing."""

    def __init__(self, response: str = "mock response"):
        self.response = response

    async def generate(self, prompt: str) -> str:
        return self.response


def test_llm_factory_string_providers():
    openai_llm = create_llm("openai")
    assert openai_llm.__class__.__name__ == "OpenAI"

    gemini_llm = create_llm("gemini")
    assert gemini_llm.__class__.__name__ == "Gemini"

    anthropic_llm = create_llm("anthropic")
    assert anthropic_llm.__class__.__name__ == "Anthropic"


def test_llm_factory_passthrough():
    mock_instance = MockLLM("test response")
    result = create_llm(mock_instance)
    assert result is mock_instance


def test_llm_factory_unknown_provider():
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        create_llm("unknown_provider")


@pytest.mark.asyncio
async def test_mock_llm_protocol():
    mock = MockLLM("test output")
    result = await mock.generate("test prompt")
    assert result == "test output"


@pytest.mark.asyncio
async def test_llm_protocol_compliance():
    providers = ["openai", "gemini", "anthropic"]

    for provider in providers:
        llm_instance = create_llm(provider)
        assert isinstance(llm_instance, LLM)
        assert hasattr(llm_instance, "generate")
        assert callable(llm_instance.generate)
