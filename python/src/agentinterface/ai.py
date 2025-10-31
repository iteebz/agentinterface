"""Agent UI component generation."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional, Union

from .callback import Callback
from .llms import LLM, create_llm

logger = logging.getLogger(__name__)

DEFAULT_INTERACTION_TIMEOUT = 300


def protocol(components: Optional[list[str]] = None) -> str:
    """Generate LLM component instructions from registry or component list."""
    if components:
        component_specs = [f"{comp}: Component" for comp in components]
    else:
        registry_path = Path.cwd() / "ai.json"
        component_specs = []

        if registry_path.exists():
            try:
                registry = json.loads(registry_path.read_text())
                components_data = registry.get("components", {})

                if not components_data:
                    logger.warning("Empty component registry. Run 'npx agentinterface discover'")
                    component_specs = ["markdown: Text content with formatting"]
                else:
                    for comp_type, comp_info in components_data.items():
                        desc = comp_info.get("description", "")
                        schema = comp_info.get("schema", {})
                        properties = schema.get("properties", {})

                        key_props = [
                            prop
                            for prop, info in list(properties.items())[:3]
                            if not info.get("optional", False)
                        ]
                        prop_hint = f" (uses: {', '.join(key_props)})" if key_props else ""
                        component_specs.append(f"{comp_type}: {desc}{prop_hint}")

            except Exception as e:
                logger.warning(f"Invalid ai.json: {e}. Run 'npx agentinterface discover'")
                component_specs = ["markdown: Text content with formatting"]
        else:
            logger.warning("No ai.json found. Run 'npx agentinterface discover'")
            component_specs = ["markdown: Text content with formatting"]

    component_list = "\n".join(f"- {spec}" for spec in component_specs)

    return f"""Available components:
{component_list}

Composition patterns:
- Single: [{{"type": "card", "data": {{"title": "Revenue", "value": "$5M"}}}}]
- Multiple: [{{"type": "card", "data": {{...}}}}, {{"type": "table", "data": {{...}}}}]
- Horizontal: [[{{"type": "card", "data": {{...}}}}, {{"type": "card", "data": {{...}}}}]]
- Mixed: [{{"type": "card", "data": {{...}}}}, [comp1, comp2], {{"type": "markdown", "data": {{...}}}}]

Return JSON array format only."""


def _extract_text(event: Any) -> str:
    """Extract text from event (str, dict, or object with text attrs)."""
    if isinstance(event, str):
        return event
    if isinstance(event, dict):
        for key in ["content", "text", "message", "output", "data"]:
            if key in event and event[key]:
                return str(event[key])
    for attr in ["content", "text", "message", "output"]:
        if hasattr(event, attr) and (val := getattr(event, attr)):
            return str(val)
    return ""


def ai(
    agent: Any,
    llm: Union[str, LLM],
    components: Optional[list[str]] = None,
    callback: Optional[Callback] = None,
    timeout: int = DEFAULT_INTERACTION_TIMEOUT,
) -> Callable:
    """Universal agent-to-UI wrapper."""
    llm_instance = create_llm(llm) if isinstance(llm, str) else llm

    def enhanced(*agent_args, **agent_kwargs):
        agent_output = agent(*agent_args, **agent_kwargs)

        if hasattr(agent_output, "__aiter__"):
            return _stream(
                agent,
                agent_output,
                llm_instance,
                components,
                callback,
                agent_args,
                agent_kwargs,
                timeout,
            )
        elif asyncio.iscoroutine(agent_output):
            return _async(agent, agent_output, llm_instance, components, agent_args, agent_kwargs)
        else:
            return _sync(agent, agent_output, llm_instance, components, agent_args, agent_kwargs)

    return enhanced


async def _generate_components(
    text: str,
    agent_args: tuple[Any, ...],
    agent_kwargs: dict[str, Any],
    components: Optional[list[str]],
    llm: LLM,
) -> list[dict[str, Any]]:
    """Generate components from text via shaper LLM."""
    from .shaper import shape

    try:
        query_context = (
            str(agent_args[0]) if agent_args else agent_kwargs.get("query", "User request")
        )
        shaped = await shape(text, {"query": query_context, "components": components}, llm)
        return json.loads(shaped)
    except Exception as e:
        logger.warning(f"Component generation failed, falling back: {e}")
        if components and "markdown" not in components:
            if isinstance(e, ValueError) and e.__cause__:
                raise e.__cause__ from None
            raise
        return [{"type": "markdown", "data": {"content": text}}]


async def _stream(
    agent: Any,
    stream: Any,
    llm: LLM,
    components: Optional[list[str]],
    callback: Optional[Callback],
    agent_args: tuple[Any, ...],
    agent_kwargs: dict[str, Any],
    timeout: int,
):
    """Streaming: Passthrough + Collect + Tack-on."""
    collected_text = ""

    async for event in stream:
        yield event
        if text := _extract_text(event):
            collected_text += text + " "

    if not collected_text.strip():
        return

    component_array = await _generate_components(
        collected_text.strip(), agent_args, agent_kwargs, components, llm
    )

    if callback:
        yield {
            "type": "component",
            "data": {"components": component_array, "callback_url": callback.endpoint()},
        }

        try:
            user_event = await callback.await_interaction(timeout=timeout)
            query_context = (
                str(agent_args[0]) if agent_args else agent_kwargs.get("query", "User request")
            )
            continuation_query = f"{query_context}\n\nUser selected: {user_event['data']}"
            continuation_agent = ai(agent, llm, components)
            async for event in continuation_agent(
                continuation_query, *agent_args[1:], **agent_kwargs
            ):
                yield event
        except asyncio.TimeoutError:
            logger.warning("User interaction timed out")
    else:
        yield {"type": "component", "data": {"components": component_array}}


async def _async(
    agent: Any,
    coroutine: Awaitable[Any],
    llm: LLM,
    components: Optional[list[str]],
    agent_args: tuple[Any, ...],
    agent_kwargs: dict[str, Any],
) -> tuple[Any, list[dict[str, Any]]]:
    """Async agent: returns (text, components) tuple."""
    response = await coroutine
    component_array = await _generate_components(
        str(response), agent_args, agent_kwargs, components, llm
    )
    return (response, component_array)


def _sync(
    agent: Any,
    response: Any,
    llm: LLM,
    components: Optional[list[str]],
    agent_args: tuple[Any, ...],
    agent_kwargs: dict[str, Any],
) -> Awaitable[tuple[Any, list[dict[str, Any]]]]:
    """Sync agent: returns coroutine resolving to (text, components) tuple."""

    async def _shape():
        component_array = await _generate_components(
            str(response), agent_args, agent_kwargs, components, llm
        )
        return (response, component_array)

    return _shape()


__all__ = ["ai", "protocol"]
