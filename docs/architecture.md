# Architecture

High-level system design.

## Core Pattern

```
Agent text → Shaper LLM → Component JSON → React UI
```

Four independent layers:
1. **Agent** - Any callable (sync/async/streaming)
2. **Shaper** - LLM selecting components from registry
3. **Registry** - Component metadata (ai.json)
4. **Renderer** - Recursive JSON → React

Domain logic, component selection, UI rendering stay separated.

## Components

### Metadata Contract

Component implementation exports alongside metadata:

```tsx
export const Card = ({ title, content }) => (
  <div><h3>{title}</h3><p>{content}</p></div>
);

export const metadata = {
  type: 'card',
  description: 'Generic card layout',
  schema: {
    type: 'object',
    properties: {
      title: { type: 'string' },
      content: { type: 'string' }
    },
    required: ['title', 'content']
  },
  category: 'layout'
};
```

Metadata enables automatic LLM instruction generation from actual component capabilities.

### Discovery

```bash
npx agentinterface discover
```

Scans `src/ai/*.tsx` → validates schemas → generates `ai.json` → Python reads registry.

LLM instructions always match actual components. Add component → autodiscover → immediately available.

### Schema-Driven Instructions

```python
def protocol(components: Optional[list[str]] = None) -> str:
    registry = json.loads(Path("ai.json").read_text())
    
    for comp_type, comp_info in registry["components"].items():
        schema = comp_info["schema"]
        required = schema.get("required", [])
        specs.append(f"{comp_type}: {desc} (requires: {', '.join(required)})")
    
    return f"""Available components:
- {chr(10).join(specs)}

Composition: [comp1, comp2] = vertical, [[comp1, comp2]] = horizontal
Return JSON array only."""
```

Instructions derived from schemas, not hardcoded. Registry is source of truth.

## Composition

### Array-Based Layout

```tsx
// Single component
{"type": "card", "data": {...}}

// Vertical stack (array)
[card1, card2, card3]

// Horizontal grid (nested array)
[[card1, card2, card3]]

// Mixed layout
[
  card1,              // Full width
  [card2, card3],     // Side by side  
  card4               // Full width
]

// Infinite nesting
[card1, [card2, [card3, card4]]]
```

### Recursive Rendering

Renderer processes arrays recursively:
- Array → vertical stack (`flex flex-col gap-6`)
- Nested array → horizontal grid (`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`)
- Component data → recursive processing (components can nest anywhere)

No layout DSL. Just arrays. Infinite composition depth.

## Callbacks

### Protocol Interface

```python
@runtime_checkable
class Callback(Protocol):
    async def await_interaction(self, timeout: int = 300) -> dict: ...
    def endpoint(self) -> str: ...
```

Two methods. Any transport (HTTP, WebSocket, SSE, custom).

### HTTP Implementation

```python
class Http(Callback):
    def __init__(self, id: str = None, port: int = 8228):
        self.id = id or str(uuid.uuid4())
        self._server = _get_shared_server(port)
    
    async def await_interaction(self, timeout: int = 300) -> dict:
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._server.callbacks[self.id] = (loop, future)
        
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
            self._server.callbacks.pop(self.id, None)
    
    def endpoint(self) -> str:
        host = os.getenv("AI_CALLBACK_HOST", "localhost")
        return f"http://{host}:{self._server.port}/callback/{self.id}"
```

**Patterns:**
- Shared server per port (multi-user efficiency)
- Lazy registration (register only when awaiting)
- Self-cleanup (automatic removal on completion/timeout)
- Background cleanup (abandoned callbacks cleaned after 600s)

### Conversation Flow

```python
async def _stream(agent, stream, llm, components, callback, args, timeout):
    collected_text = ""
    
    # Passthrough agent events
    async for event in stream:
        yield event
        if text := _extract_text(event):
            collected_text += text + " "
    
    # Generate components
    component_array = await _generate_components(collected_text.strip(), args, components, llm)
    
    # Emit components with callback URL
    if callback:
        yield {"type": "component", "data": {"components": component_array, "callback_url": callback.endpoint()}}
        
        # Wait for user interaction
        user_event = await callback.await_interaction(timeout=timeout)
        
        # Continue agent with interaction context
        continuation_query = f"{args[0]}\n\nUser selected: {user_event['data']}"
        async for event in ai(agent, llm, components, Http())(continuation_query, *args[1:]):
            yield event
    else:
        yield {"type": "component", "data": {"components": component_array}}
```

Passthrough → Collect → Generate → Wait → Continue. Infinite conversation loop.

## Agent Enhancement

### Universal Wrapper

```python
def ai(agent, llm, components=None, callback=None, timeout=300):
    def enhanced(*args, **kwargs):
        output = agent(*args, **kwargs)
        
        if hasattr(output, "__aiter__"):
            return _stream(agent, output, llm, components, callback, args, timeout)
        elif asyncio.iscoroutine(output):
            return _async(agent, output, llm, components, args)
        else:
            return _sync(agent, output, llm, components, args)
    
    return enhanced
```

Polymorphic handling. Same interface for sync, async, streaming agents.

## Design Decisions

**Why schema-driven?**
LLM instructions generated from ai.json. Add component → autodiscover → automatically available to LLM. Single source of truth.

**Why recursive composition?**
Nested arrays enable arbitrary layouts without DSL. Infinite flexibility. Simple mental model.

**Why protocol-based callbacks?**
Interface decouples transport. Easy to add WebSocket, SSE, custom transports without changing agent code.

**Why lazy registration?**
Register callbacks only when `await_interaction()` called. Prevents memory leaks from abandoned callbacks.

## Error Handling

**Fail-fast:**
```python
raise ValueError(f"Invalid JSON from LLM: {e}")
raise ValueError(f"Component '{type}' missing required fields: {missing}")
```

**Graceful degradation:**
```python
# Malformed registry → markdown fallback
# LLM failure → original text passthrough  
# Unknown component → visible error
```

Errors visible and immediate. System works without perfect conditions.

## Performance

- **Component resolution:** O(1) hash lookup
- **Registry loading:** Lazy load, cache forever
- **Server sharing:** Multiple callbacks per port
- **Cleanup:** Automatic on completion, timeout, or 600s abandonment