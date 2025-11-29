"""LLM providers with key rotation."""

import logging
import os
import time
from pathlib import Path
from typing import Any, Callable, Optional, Protocol, Union, runtime_checkable

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv

    load_dotenv(override=True)
except ImportError:
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip("\"'"))

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

        if key := os.getenv(f"{self.service}_API_KEY"):
            keys.append(key)

        for i in range(1, 11):
            if key := os.getenv(f"{self.service}_API_KEY_{i}"):
                keys.append(key)

        aliases = []
        if self.service == "GEMINI":
            aliases = ["GOOGLE_API_KEY"]
        elif self.service == "ANTHROPIC":
            aliases = ["CLAUDE_API_KEY"]

        for alias in aliases:
            if (key := os.getenv(alias)) and key not in keys:
                keys.append(key)
            for i in range(1, 11):
                if (key := os.getenv(f"{alias}_{i}")) and key not in keys:
                    keys.append(key)

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
            logger.debug(f"Rotated {self.service} key to index {self.idx}")
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
            raise ImportError(f"No {service} keys found")

        try:
            return await fn(key, *args, **kwargs)
        except Exception as e:
            err = e
            logger.warning(f"{service} request failed: {e}")
            if not rot.rotate(str(e)):
                break

    logger.error(f"All {service} attempts failed")
    raise err


@runtime_checkable
class LLM(Protocol):
    """LLM provider interface for component shaping."""

    async def generate(self, prompt: str) -> str:
        """Generate text response from prompt."""
        ...


def create_llm(provider: Union[str, LLM] = "openai") -> LLM:
    """Create or pass through LLM provider."""

    if isinstance(provider, LLM):
        return provider

    if provider == "openai":
        return OpenAI()
    elif provider == "gemini":
        return Gemini()
    elif provider == "anthropic":
        return Anthropic()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


class OpenAI(LLM):
    """OpenAI LLM provider."""

    def __init__(self, model: Optional[str] = None):
        self.model = model or "gpt-4.1-mini"

    async def generate(self, prompt: str) -> str:
        try:
            import openai
        except ImportError:
            raise ImportError("pip install openai") from None

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


class Gemini(LLM):
    """Gemini LLM provider."""

    def __init__(self, model: Optional[str] = None):
        self.model = model or "gemini-2.5-flash"

    async def generate(self, prompt: str) -> str:
        try:
            import google.genai as genai
        except ImportError:
            raise ImportError("pip install google-genai") from None

        async def _gen(key: str) -> str:
            client = genai.Client(api_key=key)
            resp = await client.aio.models.generate_content(model=self.model, contents=prompt)
            return resp.text

        return await with_rotation("gemini", _gen)


class Anthropic(LLM):
    """Anthropic LLM provider."""

    def __init__(self, model: Optional[str] = None):
        self.model = model or "claude-4.5-sonnet-latest"

    async def generate(self, prompt: str) -> str:
        try:
            import anthropic
        except ImportError:
            raise ImportError("pip install anthropic") from None

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
