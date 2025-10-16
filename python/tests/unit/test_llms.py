"""LLM factory unit tests - rotation logic, key loading, provider contracts."""

import os
from unittest.mock import MagicMock, patch

import pytest

from agentinterface.llms import LLM, Rotator, create_llm, detect_api_key


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


def test_rotator_init():
    with patch.dict(os.environ, {"OPENAI_API_KEY_1": "key1"}):
        rot = Rotator("openai")
        assert rot.service == "OPENAI"
        assert rot.keys == ["key1"]
        assert rot.idx == 0


def test_rotator_load_single_key():
    with patch.dict(os.environ, {"GEMINI_API_KEY_1": "single_key"}, clear=True):
        rot = Rotator("gemini")
        assert "single_key" in rot.keys


def test_rotator_load_multiple_keys():
    env = {
        "ANTHROPIC_API_KEY_1": "key1",
        "ANTHROPIC_API_KEY_2": "key2",
        "ANTHROPIC_API_KEY_3": "key3",
    }
    with patch.dict(os.environ, env, clear=False):
        rot = Rotator("anthropic")
        assert rot.keys == ["key1", "key2", "key3"]


def test_rotator_key_property():
    with patch.dict(os.environ, {"OPENAI_API_KEY_1": "key1"}, clear=False):
        rot = Rotator("openai")
        assert rot.key == "key1"

        rot.idx = 0
        assert rot.key == "key1"


def test_rotator_key_empty():
    with patch.dict(os.environ, {}, clear=True):
        rot = Rotator("openai")
        assert rot.key is None


def test_rotator_rotate_requires_multiple_keys():
    with patch.dict(os.environ, {"OPENAI_API_KEY_1": "key1"}, clear=True):
        rot = Rotator("openai")
        result = rot.rotate("rate limit")
        assert result is False


def test_rotator_rotate_on_quota_signal():
    env = {
        "OPENAI_API_KEY_1": "key1",
        "OPENAI_API_KEY_2": "key2",
    }
    with patch.dict(os.environ, env, clear=True):
        rot = Rotator("openai")
        rot.last = 0
        result = rot.rotate("quota exceeded: request limit")
        assert result is True
        assert rot.idx == 1


def test_rotator_rotate_signals():
    env = {
        "OPENAI_API_KEY_1": "key1",
        "OPENAI_API_KEY_2": "key2",
    }
    signals = ["quota", "rate limit", "429", "throttle", "exceeded"]
    with patch.dict(os.environ, env, clear=True):
        for signal in signals:
            rot = Rotator("openai")
            rot.last = 0
            result = rot.rotate(f"Error: {signal}")
            assert result is True, f"Failed on signal: {signal}"


def test_rotator_rotate_ignores_non_rate_errors():
    env = {
        "OPENAI_API_KEY_1": "key1",
        "OPENAI_API_KEY_2": "key2",
    }
    with patch.dict(os.environ, env, clear=True):
        rot = Rotator("openai")
        rot.last = 0
        result = rot.rotate("Unauthorized: invalid API key")
        assert result is False


def test_rotator_rotate_none_error():
    env = {
        "OPENAI_API_KEY_1": "key1",
        "OPENAI_API_KEY_2": "key2",
    }
    with patch.dict(os.environ, env, clear=True):
        rot = Rotator("openai")
        rot.last = 0
        result = rot.rotate(None)
        assert result is False


def test_rotator_rotate_throttle_cooldown():
    import time

    env = {
        "OPENAI_API_KEY_1": "key1",
        "OPENAI_API_KEY_2": "key2",
    }
    with patch.dict(os.environ, env, clear=True):
        rot = Rotator("openai")
        rot.last = time.time()
        result = rot.rotate("rate limit")
        assert result is False


def test_rotator_rotate_wraps_around():
    env = {
        "OPENAI_API_KEY_1": "key1",
        "OPENAI_API_KEY_2": "key2",
    }
    with patch.dict(os.environ, env, clear=True):
        rot = Rotator("openai")
        rot.last = 0
        rot.idx = 1
        rot.rotate("rate limit")
        assert rot.idx == 0


def test_detect_api_key_primary_pattern():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "primary_key"}, clear=True):
        key = detect_api_key("openai")
        assert key == "primary_key"


def test_detect_api_key_rotation_pattern():
    with patch.dict(
        os.environ,
        {"OPENAI_API_KEY_1": "rot1", "OPENAI_API_KEY_2": "rot2"},
        clear=True,
    ):
        key = detect_api_key("openai")
        assert key in ["rot1", "rot2"]


def test_detect_api_key_gemini_alias():
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "google_key"}, clear=True):
        key = detect_api_key("gemini")
        assert key == "google_key"


def test_detect_api_key_anthropic_alias():
    with patch.dict(os.environ, {"CLAUDE_API_KEY": "claude_key"}, clear=True):
        key = detect_api_key("anthropic")
        assert key == "claude_key"


def test_detect_api_key_none():
    with patch.dict(os.environ, {}, clear=True):
        key = detect_api_key("openai")
        assert key is None
