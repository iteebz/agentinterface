"""Agent UI component generation."""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional

from .callback import Http
from .constants import TIMEOUT
from .logger import logger



def protocol(components: Optional[List[str]] = None) -> str:
    """Generate rich LLM instructions from ai.json registry"""
    # Load component registry from ai.json
    registry_path = Path.cwd() / "ai.json"
    if not registry_path.exists():
        raise RuntimeError("ai.json not found. Run 'npx agentinterface discover' to generate component registry.")
    
    try:
        registry = json.loads(registry_path.read_text())
        registry_components = registry.get("components", {})
    except Exception as e:
        raise RuntimeError(f"Failed to load ai.json: {e}")
    
    if not registry_components:
        raise RuntimeError("No components found in ai.json. Run 'npx agentinterface discover' to generate registry.")

    # Filter components if requested
    if components:
        available_components = {k: v for k, v in registry_components.items() if k in components}
    else:
        available_components = registry_components

    # Generate rich instructions
    instructions = "# Available Components\n\n"
    instructions += f"Available components: {', '.join(sorted(available_components.keys()))}\n\n"
    instructions += "## Component Usage\n"
    instructions += 'Single: {"type": "card", "data": {"title": "Hello"}}\n'
    instructions += (
        "Arrays: [comp1, [comp2, comp3], comp4] = vertical stack with horizontal row\n\n"
    )
    instructions += "## Components\n\n"

    # Group components by category
    by_category = {}
    for comp_type, meta in available_components.items():
        category = meta.get("category", "general")
        if category not in by_category:
            by_category[category] = []
        by_category[category].append((comp_type, meta))

    # Output components by category
    for category, comps in by_category.items():
        instructions += f"### {category.capitalize()} Components\n\n"
        for comp_type, meta in comps:
            instructions += f"**{comp_type}** - {meta['description']}\n"
            if meta.get("schema", {}).get("properties"):
                for prop, info in meta["schema"]["properties"].items():
                    required = (
                        "required" if prop in meta["schema"].get("required", []) else "optional"
                    )
                    prop_type = info.get("type", "any")
                    instructions += f"- {prop} ({prop_type}, {required})"
                    if info.get("enum"):
                        instructions += f" - options: {', '.join(info['enum'])}"
                    instructions += "\n"
            instructions += "\n"

    instructions += "\nALWAYS return JSON array format.\n"
    return instructions


async def shape(response: str, context: dict = None, llm=None) -> str:
    """Transform text → components"""
    if not llm:
        from .llms import llm as create_llm

        llm = create_llm()
    from .shaper import shape

    return await shape(response, context, llm)


# Callback handling moved to callback.py module


async def _get_agent_response(agent, query: str) -> str:
    """Get response from agent"""
    if callable(agent):
        return await agent(query) if asyncio.iscoroutinefunction(agent) else agent(query)
    elif hasattr(agent, "run"):
        return (
            await agent.run(query) if asyncio.iscoroutinefunction(agent.run) else agent.run(query)
        )
    else:
        raise ValueError("Agent must be callable or have .run() method")


def _extract_text(event) -> str:
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
    agent, llm, components: Optional[List[str]] = None, port: int = 8228, interactive: bool = False
):
    """Agent → UI components"""

    def agent_fn(*agent_args, **agent_kwargs):
        agent_output = agent(*agent_args, **agent_kwargs)

        if hasattr(agent_output, "__aiter__"):
            return _stream(agent, agent_output, llm, components, port, interactive, agent_args)

        elif asyncio.iscoroutine(agent_output):
            return _async(agent, agent_output, llm, components, port, agent_args)

        else:
            return _sync(agent, agent_output, llm, components, port, agent_args)

    return agent_fn


async def _generate_components(text: str, agent_args, components, llm):
    """Core component generation logic"""
    try:
        query_context = str(agent_args[0]) if agent_args else "User request"
        shaped = await shape(text, {"query": query_context, "components": components}, llm)
        component_array = json.loads(shaped)
        return component_array
    except Exception as e:
        logger.warning(f"Component generation failed, falling back to prose: {e}")
        return [{"type": "prose", "data": {"content": text}}]


async def _stream(agent, stream, llm, components, port, interactive, agent_args):
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

        if interactive:
            # Create self-managing callback
            callback = Http(port=port)
            component_data = {
                "components": component_array,
                "callback_url": callback.endpoint(),
            }

            yield {"type": "component", "data": component_data}

            try:
                # Await user interaction - cleans up automatically
                user_event = await callback.await_interaction(timeout=TIMEOUT)
                query_context = str(agent_args[0]) if agent_args else "User request"
                continuation_query = f"{query_context}\n\nUser selected: {user_event['data']}"
                continuation_agent = ai(agent, llm, components, port, interactive)
                async for event in continuation_agent(continuation_query, *agent_args[1:]):
                    yield event
            except asyncio.TimeoutError:
                logger.warning("User interaction timed out")
        else:
            yield {"type": "component", "data": {"components": component_array}}


async def _async(agent, coroutine, llm, components, port, agent_args):
    """Async - always returns (text, components) tuple"""
    response = await coroutine
    component_array = await _generate_components(str(response), agent_args, components, llm)
    return (response, component_array)


def _sync(agent, response, llm, components, port, agent_args):
    """Sync - always returns coroutine that resolves to (text, components) tuple"""

    async def _async_shape():
        component_array = await _generate_components(str(response), agent_args, components, llm)
        return (response, component_array)

    return _async_shape()


__all__ = ["ai", "protocol", "shape"]
