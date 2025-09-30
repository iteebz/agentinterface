"""Agent text to component JSON."""

import json
from pathlib import Path
from typing import Any, Iterable, Optional

from .llms import LLM
from .logger import logger

_REGISTRY_CACHE: Optional[dict[str, Any]] = None


def _load_registry() -> dict[str, Any]:
    """Search upward for ai.json like git searches for .git."""
    current = Path.cwd()
    for path in [current, *current.parents]:
        registry_path = path / "ai.json"
        if registry_path.exists():
            break
    else:
        logger.warning("Component registry ai.json not found")
        return {}

    try:
        data = json.loads(registry_path.read_text())
        components = data.get("components", {})
        if not isinstance(components, dict):
            raise ValueError("components key must be object")
        return components
    except Exception as exc:
        logger.warning(f"Failed to load component registry: {exc}")
        return {}


def _registry() -> dict[str, Any]:
    """Cached registry accessor."""
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is None:
        _REGISTRY_CACHE = _load_registry()
    return _REGISTRY_CACHE


def _validate_component_tree(components: Any, allowed: Optional[Iterable[str]] = None) -> None:
    """Validate component tree structure and required fields."""
    if not isinstance(components, list):
        raise ValueError("LLM output must be a JSON array")

    allowed_set = set(allowed or []) or None
    registry = _registry()

    def _validate(node: Any, trail: str) -> None:
        if isinstance(node, list):
            for idx, child in enumerate(node):
                _validate(child, f"{trail}[{idx}]")
            return

        if not isinstance(node, dict):
            raise ValueError(f"Component at {trail} must be an object")

        comp_type = node.get("type")
        if not isinstance(comp_type, str) or not comp_type:
            raise ValueError(f"Component at {trail} missing string 'type'")

        if allowed_set is not None and comp_type not in allowed_set:
            raise ValueError(f"Component type '{comp_type}' not permitted in context")

        schema_entry = registry.get(comp_type)
        if schema_entry is None and registry:
            raise ValueError(f"Unknown component type '{comp_type}'")

        data = node.get("data", {})
        if data is None:
            data = {}
        if not isinstance(data, dict):
            raise ValueError(f"Component '{comp_type}' data must be an object")

        required_fields = []
        if schema_entry:
            schema = schema_entry.get("schema", {})
            required_fields = schema.get("required", []) if isinstance(schema, dict) else []

        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValueError(
                f"Component '{comp_type}' missing required data fields: {', '.join(sorted(missing))}"
            )

    for index, item in enumerate(components):
        _validate(item, f"components[{index}]")


def _strip_markdown_fences(text: str) -> str:
    """Strip markdown code fences from LLM output."""
    if "```json" in text:
        return text.split("```json")[1].split("```")[0].strip()
    if "```" in text:
        return text.split("```")[1].strip()
    return text


async def shape(
    response: str, context: Optional[dict[str, Any]] = None, llm: Optional[LLM] = None
) -> str:
    """Transform agent text into component JSON via shaper LLM."""
    if not llm:
        return response
    return await _generate_component(response, context or {}, llm)


async def _generate_component(response: str, context: dict[str, Any], llm: LLM) -> str:
    """Generate component JSON from text using shaper LLM."""
    from .ai import protocol

    available_components = context.get("components")
    instructions = protocol(available_components)

    prompt = f"""Transform this content into a component JSON array:

{response}

{instructions}"""

    result = await llm.generate(prompt)
    result = _strip_markdown_fences(result)

    try:
        components = json.loads(result)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}") from e

    if not isinstance(components, list):
        raise ValueError("LLM must return array")

    allowed_components = context.get("components") if context else None
    _validate_component_tree(components, allowed_components)
    return json.dumps(components, indent=2)
