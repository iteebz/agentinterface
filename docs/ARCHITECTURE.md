# Architecture

**Core components:** Shaper LLM, component autodiscovery, callbacks, recursive rendering

## System Design

**Agent Response → Shaper LLM Analysis → Component Selection → UI Rendering**

```python
agent = ai(agent, llm)
result = await agent("Show sales data")
# Returns: (text, components) or async generator with component events
```

## Core Components

### Response Shaper
```python
# Python: agentinterface/shaper.py
async def shape(response: str, context: dict, llm) -> str:
    # Transform text → component JSON via LLM
    return await _generate_component(response, context, llm)
```

**Function:** Text → structured component selection

### Component Registry  
```typescript
// Auto-generated from component metadata
const COMPONENTS = {
  card: Card,
  table: Table,
  timeline: Timeline,
  // ... discovered via npx agentinterface discover
};
```

**Function:** Type string → React component mapping

### Recursive Renderer
```typescript
// From render.tsx
function render(agentJSON: string, components): React.ReactNode {
  function renderItem(item: any): React.ReactNode {
    if (Array.isArray(item)) {
      return <div className="flex gap-4">{/* Horizontal */}</div>;
    }
    
    const Component = components[item.type];
    return <Component {...processData(item.data)} />;
  }
  
  const parsed = JSON.parse(agentJSON);
  return renderItem(parsed);
}
```

**Function:** JSON → nested React components

## Component Discovery System

### Metadata Pattern
```typescript
// Every component exports metadata
export const metadata = {
  type: 'card',
  description: 'Generic card layout',
  schema: { /* JSON Schema */ },
  category: 'layout'
};
```

### Autodiscovery Process
```javascript
// scripts/discover.mjs
1. Scan .tsx files for metadata exports
2. Extract schema + description via AST parsing
3. Generate ai.json registry and ai.tsx wrapper
4. Components automatically available to shaper LLM
5. Protocol() dynamically generates LLM instructions from ai.json
```

## Bidirectional Communication

### Callback Protocol
```python
# callback.py
@runtime_checkable
class Callback(Protocol):
    async def await_interaction(self, timeout: int = 300) -> dict:
        """Wait for user interaction."""
        ...
    
    def endpoint(self) -> str:
        """Get endpoint URL."""
        ...
```

### Interaction Flow
```
1. Component includes callback endpoint
2. User interacts with component
3. Component sends data to endpoint
4. Awaiting agent receives data
5. Agent continues with user choice
```

## Composition System

### Layout Rules
- **Arrays:** Horizontal layout (`flex gap-4`)
- **Nested objects:** Infinite component depth
- **Data processing:** Recursive component resolution

### Example Composition
```json
[
  {"type": "card", "data": {"title": "Overview"}},
  [
    {"type": "table", "data": {...}},
    {"type": "insights", "data": {...}}
  ]
]
```

**Renders:** Card above, table + insights side-by-side

## Shaper LLM Protocol

### Component Selection Logic
```python
prompt = f"""Transform agent response into UI components.

=== AGENT RESPONSE ===
{response}

=== AVAILABLE COMPONENTS ===
{component_registry}

Return JSON array. Components can contain other components.
"""
```

**Function:** Shaper LLM converts text to components using context

## Technical Elegance

**Separation of Concerns:**
- **Agent:** Domain knowledge
- **Shaper:** Component selection
- **Renderer:** Component instantiation

**Universal Compatibility:**
- Framework-agnostic
- Zero agent modification
- Text fallback

**Extensibility:**
- Metadata exports
- Auto-discovery
- Type safety

**Zero Friction:**
- `ai()` wrapper
- Auto-discovery
- Built-in callbacks