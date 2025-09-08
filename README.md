# AgentInterface

Agents choose components. Universal agent wrapper.

**Core flow:** Agent → Shaper LLM → Component JSON → React UI

```bash
npm install agentinterface
```

```python
pip install agentinterface
```

## Tool → UI Reasoning Pattern

Agents reason about which tools to use. Same pattern for UI components:

```python
# Manual parsing: O(components × responses)
if "table" in response: render_table(parse_data(response))
if "chart" in response: render_chart(parse_data(response))

# Component reasoning: O(1)
enhanced = ai(agent, llm="gemini")
text, components = await enhanced("Show Q3 sales")
# Returns components: [{"type": "table", "data": {...}}]
```

Shaper LLM selects components based on content analysis:

```python
# Works with any agent: OpenAI, Anthropic, custom
enhanced = ai(agent, llm="gemini")  
result = await enhanced("Show Q3 sales data")
# Returns: (text, components) - preserves original output
```

## Key Differentiators

**vs Direct artifacts:**
- Universal: Works with any agent
- Bidirectional: Components include callbacks
- Compositional: Multiple components per response
- Dynamic: Stream with component injection

**vs Manual Parsing:**
- Automatic component selection via LLM reasoning
- Zero parsing logic required

## Architecture

1. **Agent responds** - Text output
2. **Shaper LLM** - Component selection
3. **Components render** - JSON → React interface

```python
from agentinterface import ai

# Curried pattern
enhanced = ai(your_agent, llm="gemini")
result = await enhanced("Show Q3 sales")
# Returns: [{"type": "table", "data": {...}}]
```

## Component Registry

```bash
npx agentinterface discover  # Generates ai.json
```

Scans your codebase, extracts metadata, generates LLM-readable schemas.

## Component Types

**Layout:** `card`, `accordion`, `tabs`  
**Data:** `table`, `timeline`, `tree`  
**Interactive:** `suggestions`, `gallery`

## Bidirectional Interaction

```python
# Callback pattern
async for event in enhanced("Show sales data"):
    if event["type"] == "component":
        # Component → callback → continuation
        callback = event["data"]["callback_url"]
        user_event = await event["callback"]() 
        continuation = enhanced(f"User selected: {user_event["data"]}")
```

## Multi-Component Composition

```json
[
  {"type": "card", "data": {"title": "Results"}},
  [
    {"type": "table", "data": {...}},
    {"type": "insights", "data": {...}}
  ]
]
```

Arrays create vertical stacks. Nested arrays create horizontal rows.

## Custom Components

```typescript
export const metadata = {
  type: 'portfolio',
  description: 'Project showcase',
  schema: { /* JSON Schema */ }
};

export function Portfolio({ projects }) {
  return <div>{/* Component */}</div>;
}
```

```bash
npx agentinterface discover  # Auto-integrates
```

## Design Principles

**Agent**: Domain logic  
**Shaper**: Component selection  
**Renderer**: UI composition

Separation of concerns.

## License

MIT