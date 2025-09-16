"""Agent text to component JSON."""

import json
from typing import Any, Dict, Optional

from .llms import LLM


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
            return json.dumps(components, indent=2)

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Component generation failed: {e}") from e
