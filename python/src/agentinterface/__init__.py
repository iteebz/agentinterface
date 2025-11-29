"""AgentInterface - AI agents choose UI components with zero ceremony"""

__version__ = "1.0.0"
from .ai import ai, protocol
from .callback import Callback, Http
from .llms import LLM, create_llm
from .shaper import shape

__all__ = ["ai", "protocol", "shape", "create_llm", "LLM", "Callback", "Http"]
