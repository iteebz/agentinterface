# Architecture

Technical design and implementation patterns for AgentInterface.

## Core Abstractions

### Agent → Shaper → Registry → Renderer

**Agent**: Any callable that returns text (sync, async, streaming)  
**Shaper**: LLM that transforms text → component JSON  
**Registry**: Schema-driven component discovery (ai.json)  
**Renderer**: Recursive JSON → React composition

**Separation of concerns**: Domain logic, component selection, UI rendering remain independent.

## Component System

### Metadata-Driven Discovery

```typescript
// Component contract
export const Component = (props) => JSX.Element;
export const metadata = {
  type: 'component',
  description: 'Human/LLM readable description',
  schema: { /* JSON Schema for props */ },
  category: 'layout'
};
```

**Discovery process**:
1. AST parsing extracts metadata from .tsx files
2. Schema validation ensures consistency  
3. Registry generation (ai.json) for shaper LLM
4. Static imports in renderer (DEFAULT_COMPONENTS)

**Why metadata**: Enables automated LLM guidance generation from actual component capabilities.

### Schema-Driven Protocol

```python
def protocol(components=None):
    # Read ai.json registry
    registry = json.loads(registry_path.read_text())
    
    # Extract component specs from schemas
    for comp_type, comp_info in registry["components"].items():
        schema = comp_info.get("schema", {})
        required_props = [prop for prop, info in schema["properties"].items() 
                         if not info.get("optional", False)]
        
        component_specs.append(f"{comp_type}: {description} (uses: {required_props})")
```

**Why schema-driven**: LLM guidance reflects actual component capabilities, not hardcoded examples.

## Recursive Rendering

### Composition Rules

```typescript
// Single component
{"type": "card", "data": {...}}

// Vertical stack (array)
[component1, component2, component3]

// Horizontal row (nested array)  
[component1, [component2, component3]]

// Mixed composition (infinite nesting)
[
  {"type": "card", "data": {...}},
  [
    {"type": "table", "data": {...}},
    {"type": "timeline", "data": {...}}
  ]
]
```

**Layout mapping**:
- Arrays → `<div className="space-y-6">` (vertical)
- Nested arrays → `<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">` (horizontal)

### Data Processing

```typescript
function processData(data: any): any {
  if (data && typeof data === 'object' && data.type) {
    return renderItem(data, 0); // Nested component
  }
  if (Array.isArray(data)) {
    return data.map(item => processData(item)); // Nested array
  }
  return data; // Literal value
}
```

**Infinite composition**: Components can contain other components at any depth.

## Agent Enhancement

### Universal Wrapper Pattern

```python
def ai(agent, llm, components=None, callback=None):
    def enhanced(*args, **kwargs):
        agent_output = agent(*args, **kwargs)
        
        # Handle sync, async, streaming agents uniformly
        if hasattr(agent_output, "__aiter__"):
            return _stream(agent, agent_output, llm, components, callback, args)
        elif asyncio.iscoroutine(agent_output):
            return _async(agent, agent_output, llm, components, callback, args)
        else:
            return _sync(agent, agent_output, llm, components, callback, args)
    
    return enhanced
```

**Polymorphic handling**: Same interface works with any agent pattern (sync/async/streaming).

### Response Patterns

```python
# Sync agent → async wrapper (returns coroutine)
enhanced = ai(sync_agent, llm)
result = await enhanced("query")  # (text, components)

# Async agent → async wrapper (returns coroutine)  
enhanced = ai(async_agent, llm)
result = await enhanced("query")  # (text, components)

# Streaming agent → async generator
enhanced = ai(streaming_agent, llm)
async for event in enhanced("query"):  # Yields events + components
    ...
```

**Consistent interface**: All agents return component-enhanced outputs.

## Callback Architecture

### Protocol-Based Design

```python
@runtime_checkable
class Callback(Protocol):
    async def await_interaction(self, timeout: int = 300) -> dict: ...
    def endpoint(self) -> str: ...
```

**Extensible**: New callback implementations (WebSocket, SSE, etc.) just implement protocol.

### HTTP Implementation

```python
class Http(Callback):
    def __init__(self, id=None, port=8228):
        self._server = _get_shared_server(port)  # Singleton per port
        self._future = asyncio.Future()
        self._server.callbacks[self.id] = self._future
```

**Shared server pattern**: Multiple callbacks share HTTP server per port.

**Self-cleanup**: Callbacks remove themselves after completion/timeout.

## Error Handling

### Fail-Fast Principles

```python
# Invalid JSON from LLM
raise ValueError(f"Invalid JSON from LLM: {e}")

# Missing required props
return <div>Error: Missing required data for {type}</div>

# Unknown component type  
return <div>Unknown: {type}</div>
```

**Visible failures**: Errors appear in UI rather than silently breaking.

### Graceful Degradation

```python
# Malformed ai.json → markdown fallback
component_specs = ["markdown: Text content with formatting"]

# No custom components → DEFAULT_COMPONENTS
componentMap = components || DEFAULT_COMPONENTS

# LLM failure → original text
return response if not llm else await _generate_component(...)
```

**Progressive enhancement**: System works without perfect conditions.

## Design Decisions

### Why Not Wrapper Generation?

**Problem**: Generated ai.tsx creates import dependencies, bundle bloat, build complexity.

**Solution**: Static DEFAULT_COMPONENTS + explicit custom component maps.

**Trade-off**: Manual component importing vs automatic discovery in React.

### Why Schema-Driven Protocol?

**Problem**: Hardcoded component examples diverge from actual component capabilities.

**Solution**: Extract LLM guidance from actual component schemas in ai.json.

**Benefit**: LLM instructions always reflect current component reality.

### Why Recursive Composition?

**Problem**: Fixed layouts limit component expressiveness.

**Solution**: Nested arrays enable arbitrary component arrangements.

**Implementation**: `processData()` recursively handles component nesting.

## Performance Considerations

### Component Resolution

```typescript
// O(1) component lookup
const Component = componentMap[type];
if (!Component) return <div>Unknown: {type}</div>;
```

**Fast rendering**: Component map provides constant-time type resolution.

### Registry Loading

```python
# Lazy loading on first protocol() call
if registry_path.exists():
    registry = json.loads(registry_path.read_text())
```

**Startup optimization**: Registry only loaded when generating LLM instructions.

## Testing Strategy

### Protocol Testing

```python
def test_protocol_uses_schema_properties():
    # Test protocol() extracts actual schema properties
    assert "card: Test card component (uses: title, content)" in result
```

**Schema validation**: Tests verify protocol() uses real component schemas.

### Callback Testing  

```python  
def test_callback_cleanup_abandoned():
    # Test timeout cleanup prevents memory leaks
    assert "test-cleanup" not in server.callbacks
```

**Resource management**: Tests ensure callback cleanup works correctly.

### Rendering Testing

```typescript
test('should render components using DEFAULT_COMPONENTS', () => {
    ref.current?.addResponse(JSON.stringify([{
        type: 'markdown', data: { content: '# Test' }
    }]));
    expect(screen.getByText('Test')).toBeInTheDocument();
});
```

**Component integration**: Tests verify rendering with built-in components.