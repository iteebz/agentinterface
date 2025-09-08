"""Agent text to component JSON."""

import json
from typing import Any, Dict, Optional

from .logger import logger


async def shape(response: str, context: Dict[str, Any] = None, llm=None) -> str:
    """
    Transform agent response into AIP components

    Args:
        response: Agent's text response
        context: Query context (query, domain, user_id, etc.)
        llm: LLM provider (optional)

    Returns:
        AIP component JSON or original response
    """
    if not llm:
        return response

    context = context or {}

    try:
        component = await _generate_component(response, context, llm)
        if component:
            return component
        else:
            logger.warning("Component generation returned None, falling back to text")
            return response
    except Exception as e:
        logger.error(f"Shaping failed: {e}", exc_info=True)
        return response


async def _generate_component(response: str, context: Dict[str, Any], llm) -> Optional[str]:
    """Generate AIP component from response"""

    query = context.get("query", "")
    domain = context.get("domain", "general")

    from .ai import protocol

    available_components = context.get("components")
    instructions = protocol(available_components)

    prompt = f"""Transform to component JSON array:

{response}

Components: {', '.join(available_components or [])}

Arrays = vertical stack. Nested arrays = horizontal rows.
Return JSON like: [{{"type": "prose", "data": {{"content": "text"}}}}, [{{"type": "card", "data": {{"title": "A"}}}}, {{"type": "card", "data": {{"title": "B"}}}}]]"""

    try:
        result = await llm.generate(prompt)

        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].strip()

        components = json.loads(result)
        if isinstance(components, list):
            return json.dumps(components, indent=2)
        else:
            logger.warning("Result is not a list, cannot use as components")

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
    except Exception as e:
        logger.error(f"Component generation failed: {e}", exc_info=True)

    return None
