"""Agent text to component JSON."""

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from .llms import LLM
from .logger import logger

_REGISTRY_CACHE: Optional[Dict[str, Any]] = None


def _load_registry() -> Dict[str, Any]:
    # Search upward for ai.json like git searches for .git
    current = Path.cwd()
    for path in [current, *current.parents]:
        registry_path = path / "ai.json"
        if registry_path.exists():
            break
    else:
        logger.warning("Component registry ai.json not found; skipping schema validation")
        return {}

    try:
        data = json.loads(registry_path.read_text())
        components = data.get("components", {})
        if not isinstance(components, dict):  # pragma: no cover - defensive
            raise ValueError("components key must be object")
        return components
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning(f"Failed to load component registry: {exc}")
        return {}


def _registry() -> Dict[str, Any]:
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is None:
        _REGISTRY_CACHE = _load_registry()
    return _REGISTRY_CACHE


def _validate_component_tree(
    components: Any, allowed: Optional[Iterable[str]] = None
) -> None:
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
        if schema_entry is None:
            if registry:
                raise ValueError(f"Unknown component type '{comp_type}'")
            # If no registry data, we cannot validate schema but keep going

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
            missing_fields = ", ".join(sorted(missing))
            raise ValueError(
                f"Component '{comp_type}' missing required data fields: {missing_fields}"
            )

    for index, item in enumerate(components):
        _validate(item, f"components[{index}]")


async def shape(
    response: str, context: Optional[Dict[str, Any]] = None, llm: Optional[LLM] = None
) -> str:
    if not llm:
        return response

    component = await _generate_component(response, context or {}, llm)
    return component if component else response


async def _generate_component(response: str, context: Dict[str, Any], llm: LLM) -> Optional[str]:
    from .ai import protocol

    available_components = context.get("components")
    instructions = protocol(available_components)

    prompt = f"""Transform this content into a component JSON array:

{response}

{instructions}"""

    try:
        result = await llm.generate(prompt)

        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].strip()

        components = json.loads(result)
        if isinstance(components, list):
            allowed_components = context.get("components") if context else None
            _validate_component_tree(components, allowed_components)
            return json.dumps(components, indent=2)

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}") from e
    except ValueError:
        raise
    except Exception as e:
        raise RuntimeError(f"Component generation failed: {e}") from e
