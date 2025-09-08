"""LLM providers with key rotation."""

import os
import time
from typing import Any, Callable, Optional, Protocol, Union, runtime_checkable

from .constants import DEFAULT_MODELS, DEFAULT_PROVIDER
from .logger import logger

_rotators = {}


class Rotator:
    """Key rotator with rate limit detection."""

    def __init__(self, service: str):
        self.service = service.upper()
        self.keys = self._load()
        self.idx = 0
        self.last = 0

    def _load(self) -> list[str]:
        """Load all keys for service."""
        keys = []

        for i in range(1, 11):
            key = os.getenv(f"{self.service}_API_KEY_{i}")
            if key:
                keys.append(key)

        aliases = []
        if self.service == "GEMINI":
            aliases = ["GOOGLE_API_KEY"]
        elif self.service == "ANTHROPIC":
            aliases = ["CLAUDE_API_KEY"]

        for alias in aliases:
            for i in range(1, 11):
                key = os.getenv(f"{alias}_{i}")
                if key and key not in keys:
                    keys.append(key)

        base = detect_api_key(self.service.lower())
        if base and base not in keys:
            keys.append(base)

        return keys

    @property
    def key(self) -> Optional[str]:
        """Current key."""
        return self.keys[self.idx % len(self.keys)] if self.keys else None

    def rotate(self, err: str = None) -> bool:
        """Rotate on rate limits."""
        if not err or len(self.keys) < 2:
            return False

        signals = ["quota", "rate limit", "429", "throttle", "exceeded"]
        if not any(s in err.lower() for s in signals):
            return False

        now = time.time()
        if now - self.last >= 1:
            self.idx = (self.idx + 1) % len(self.keys)
            self.last = now
            logger.warning(f"Rotated {self.service} key to index {self.idx}")
            return True
        return False


async def with_rotation(service: str, fn: Callable, *args, **kwargs) -> Any:
    """Execute with automatic key rotation."""
    svc = service.upper()
    if svc not in _rotators:
        _rotators[svc] = Rotator(svc)

    rot = _rotators[svc]
    err = None

    for _attempt in range(3):
        key = rot.key
        if not key:
            logger.error(f"No {service} keys found")
            raise ValueError(f"No {service} keys found")

        try:
            return await fn(key, *args, **kwargs)
        except Exception as e:
            err = e
            logger.warning(f"{service} request failed: {e}")
            if not rot.rotate(str(e)):
                break

    logger.error(f"All {service} attempts failed")
    raise err


def load_env():
    """Load .env file using python-dotenv if available, fallback to manual parsing."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        from pathlib import Path

        env_file = Path(".env")
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and "=" in line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def detect_api_key(service: str) -> Optional[str]:
    """Cogency-compatible API key detection with rotation support."""
    load_env()

    patterns = [
        f"{service.upper()}_API_KEY",
        f"{service.upper()}_KEY",
        f"{service}_API_KEY",
        f"{service}_KEY",
    ]

    if service == "gemini":
        patterns.extend(["GOOGLE_API_KEY", "GOOGLE_KEY"])
    elif service == "anthropic":
        patterns.extend(["CLAUDE_API_KEY", "CLAUDE_KEY"])

    for pattern in patterns:
        if pattern in os.environ:
            return os.environ[pattern]

    for pattern in patterns:
        if pattern.endswith("_API_KEY"):
            for i in range(1, 11):
                rotation_key = f"{pattern}_{i}"
                if rotation_key in os.environ:
                    return os.environ[rotation_key]

    return None


@runtime_checkable
class LLM(Protocol):
    """LLM provider interface for component shaping."""

    async def generate(self, prompt: str) -> str:
        """Generate text response from prompt."""
        ...


def llm(provider: Union[str, LLM] = DEFAULT_PROVIDER) -> LLM:
    """Create or pass through LLM provider.

    Args:
        provider: String provider name or LLM instance

    Returns:
        LLM provider instance

    Examples:
        model = llm("openai")
        model = llm("gemini")
        model = llm("anthropic")

        class CustomLLM:
            async def generate(self, prompt: str) -> str:
                return "Custom response"

        model = llm(CustomLLM())
    """
    if hasattr(provider, "generate"):
        return provider

    if provider == "openai":
        return OpenAI()
    elif provider == "gemini":
        return Gemini()
    elif provider == "anthropic":
        return Anthropic()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


class OpenAI:
    """OpenAI LLM provider."""

    def __init__(self, model: Optional[str] = None):
        self.model = model or DEFAULT_MODELS["openai"]
        self.api_key = detect_api_key("openai")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not found")

    async def generate(self, prompt: str) -> str:
        try:
            import openai
        except ImportError:
            raise RuntimeError("pip install openai") from None

        async def _gen(key: str) -> str:
            client = openai.AsyncOpenAI(api_key=key)
            resp = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.1,
            )
            return resp.choices[0].message.content

        return await with_rotation("openai", _gen)


class Gemini:
    """Gemini LLM provider."""

    def __init__(self, model: Optional[str] = None):
        self.model = model or DEFAULT_MODELS["gemini"]
        self.api_key = detect_api_key("gemini")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not found")

    async def generate(self, prompt: str) -> str:
        try:
            import google.genai as genai
        except ImportError:
            raise RuntimeError("pip install google-genai") from None

        async def _gen(key: str) -> str:
            client = genai.Client(api_key=key)
            resp = await client.aio.models.generate_content(model=self.model, contents=prompt)
            return resp.text

        return await with_rotation("gemini", _gen)


class Anthropic:
    """Anthropic LLM provider."""

    def __init__(self, model: Optional[str] = None):
        self.model = model or DEFAULT_MODELS["anthropic"]
        self.api_key = detect_api_key("anthropic")
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not found")

    async def generate(self, prompt: str) -> str:
        try:
            import anthropic
        except ImportError:
            raise RuntimeError("pip install anthropic") from None

        async def _gen(key: str) -> str:
            client = anthropic.AsyncAnthropic(api_key=key)
            resp = await client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text

        return await with_rotation("anthropic", _gen)
