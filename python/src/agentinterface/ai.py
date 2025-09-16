"""Agent UI component generation."""

import asyncio
import json
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from .callback import Callback, Http
from .llms import LLM
from .logger import logger


def protocol(components: Optional[List[str]] = None) -> str:
    """Generate LLM component instructions"""
    if components:
        component_specs = [f"{comp}: Available component" for comp in components]
    else:
        registry_path = Path.cwd() / "ai.json"
        component_specs = []

        if registry_path.exists():
            try:
                registry = json.loads(registry_path.read_text())
                components_data = registry.get("components", {})

                if not components_data:
                    logger.warning(
                        "Empty component registry found. Run 'npx agentinterface discover' to scan for components."
                    )
                    component_specs = ["markdown: Text content with formatting"]
                else:
                    for comp_type, comp_info in components_data.items():
                        desc = comp_info.get("description", "")
                        schema = comp_info.get("schema", {})
                        properties = schema.get("properties", {})

                        # Show key properties from schema
                        key_props = []
                        for prop, prop_info in list(properties.items())[:3]:  # Show first 3 props
                            if not prop_info.get("optional", False):
                                key_props.append(prop)

                        prop_hint = f" (uses: {', '.join(key_props)})" if key_props else ""
                        component_specs.append(f"{comp_type}: {desc}{prop_hint}")

            except Exception as e:
                logger.warning(
                    f"Invalid ai.json registry: {e}. Run 'npx agentinterface discover' to regenerate."
                )
                component_specs = ["markdown: Text content with formatting"]
        else:
            logger.warning(
                "No ai.json registry found. Run 'npx agentinterface discover' to scan for components."
            )
            component_specs = ["markdown: Text content with formatting"]

    component_list = "\n".join(f"- {spec}" for spec in component_specs)

    # Use only available components in examples
    available_components = components or ["card", "table", "markdown"]
    first_comp = available_components[0] if available_components else "card"
    second_comp = available_components[1] if len(available_components) > 1 else first_comp
    third_comp = available_components[2] if len(available_components) > 2 else first_comp

    return f"""Available components:
{component_list}

Composition patterns:
- Single: [{{"type": "{first_comp}", "data": {{"title": "Revenue", "value": "$5M"}}}}]
- Multiple: [{{"type": "{first_comp}", "data": {...}}}, {{"type": "{second_comp}", "data": {...}}}]
- Horizontal: [[{{"type": "{first_comp}", "data": {...}}}, {{"type": "{first_comp}", "data": {...}}}]]
- Mixed: [{{"type": "{first_comp}", "data": {...}}}, [comp1, comp2], {{"type": "{third_comp}", "data": {...}}}]

Return JSON array format only."""


# Callback handling moved to callback.py module


async def _get_agent_response(agent: Any, query: str) -> str:
    """Get response from agent"""
    if callable(agent):
        return await agent(query) if asyncio.iscoroutinefunction(agent) else agent(query)
    elif hasattr(agent, "run"):
        return (
            await agent.run(query) if asyncio.iscoroutinefunction(agent.run) else agent.run(query)
        )
    else:
        raise ValueError("Agent must be callable or have .run() method")


def _extract_text(event: Any) -> str:
    """Extract text from any event format with zero coupling."""
    if isinstance(event, str):
        return event
    if isinstance(event, dict):
        for key in ["content", "text", "message", "output", "data"]:
            if key in event and event[key]:
                return str(event[key])
    for attr in ["content", "text", "message", "output"]:
        if hasattr(event, attr) and getattr(event, attr):
            return str(getattr(event, attr))
    str_value = str(event)
    return str_value if str_value and str_value not in ["None", "<object>", "{}"] else ""


def ai(
    agent: Any,
    llm: LLM,
    components: Optional[List[str]] = None,
    callback: Optional[Callback] = None,
    timeout: int = 300,
) -> Callable:
    """Universal agent-to-UI wrapper"""

    def enhanced(*agent_args, **agent_kwargs):
        agent_output = agent(*agent_args, **agent_kwargs)

        if hasattr(agent_output, "__aiter__"):
            return _stream(agent, agent_output, llm, components, callback, agent_args, timeout)

        elif asyncio.iscoroutine(agent_output):
            return _async(agent, agent_output, llm, components, callback, agent_args)

        else:
            return _sync(agent, agent_output, llm, components, callback, agent_args)

    return enhanced


async def _generate_components(
    text: str, agent_args: Tuple[Any, ...], components: Optional[List[str]], llm: LLM
) -> List[Dict[str, Any]]:
    """Core component generation logic"""
    from .shaper import shape

    try:
        query_context = str(agent_args[0]) if agent_args else "User request"
        shaped = await shape(text, {"query": query_context, "components": components}, llm)
        component_array = json.loads(shaped)
        return component_array
    except Exception as e:
        logger.warning(f"Component generation failed, falling back to prose: {e}")
        return [{"type": "markdown", "data": {"content": text}}]


async def _stream(
    agent: Any,
    stream: Any,
    llm: LLM,
    components: Optional[List[str]],
    callback: Optional[Callback],
    agent_args: Tuple[Any, ...],
    timeout: int = 300,
):
    """Streaming: Passthrough + Collect + Tack-on"""
    collected_text = ""

    async for event in stream:
        yield event
        text = _extract_text(event)
        if text:
            collected_text += text + " "

    if collected_text.strip():
        component_array = await _generate_components(
            collected_text.strip(), agent_args, components, llm
        )

        if callback:
            component_data = {
                "components": component_array,
                "callback_url": callback.endpoint(),
            }

            yield {"type": "component", "data": component_data}

            try:
                # Await user interaction - cleans up automatically
                user_event = await callback.await_interaction(timeout=timeout)
                query_context = str(agent_args[0]) if agent_args else "User request"
                continuation_query = f"{query_context}\n\nUser selected: {user_event['data']}"
                continuation_agent = ai(agent, llm, components, Http())
                async for event in continuation_agent(continuation_query, *agent_args[1:]):
                    yield event
            except asyncio.TimeoutError:
                logger.warning("User interaction timed out")
        else:
            yield {"type": "component", "data": {"components": component_array}}


async def _async(
    agent: Any,
    coroutine: Awaitable[Any],
    llm: LLM,
    components: Optional[List[str]],
    callback: Optional[Callback],
    agent_args: Tuple[Any, ...],
) -> Tuple[Any, List[Dict[str, Any]]]:
    """Async - always returns (text, components) tuple"""
    response = await coroutine
    component_array = await _generate_components(str(response), agent_args, components, llm)
    return (response, component_array)


def _sync(
    agent: Any,
    response: Any,
    llm: LLM,
    components: Optional[List[str]],
    callback: Optional[Callback],
    agent_args: Tuple[Any, ...],
) -> Awaitable[Tuple[Any, List[Dict[str, Any]]]]:
    """Sync - always returns coroutine that resolves to (text, components) tuple"""

    async def _async_shape():
        component_array = await _generate_components(str(response), agent_args, components, llm)
        return (response, component_array)

    return _async_shape()


__all__ = ["ai", "protocol"]
