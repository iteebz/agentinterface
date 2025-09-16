# AgentInterface

**Universal agent-to-UI wrapper.** Agents choose components via LLM reasoning.

```bash
npm install agentinterface  # React components
pip install agentinterface  # Python wrapper
```

## Core Pattern

**Agent text → Shaper LLM → Component JSON → React UI**

Instead of parsing agent responses, let a shaper LLM select appropriate components:

```python
from agentinterface import ai

# Any agent becomes component-aware
enhanced = ai(your_agent, llm="gemini")
text, components = await enhanced("Show Q3 sales")
# Returns: [{"type": "table", "data": {"headers": [...], "rows": [...]}}]
```

```typescript
import { render } from 'agentinterface';

// Component JSON → React UI
<div>{render(JSON.stringify(components))}</div>
```

## Quick Start

### Python: Enhance Any Agent

```python
from agentinterface import ai

async def sales_agent(query: str) -> str:
    return "Q3 revenue up 15%. Key metrics: $2M revenue, 10K users."

# Add component generation
enhanced = ai(sales_agent, llm="gemini")
result = await enhanced("Show Q3 dashboard")
# Returns: (text, components)
```

### React: Render Components

```typescript
import { render } from 'agentinterface';

function Dashboard({ components }) {
  return <div>{render(components)}</div>;
}
```

**Built-in components:** `card`, `table`, `timeline`, `accordion`, `tabs`, `markdown`, `suggestions`, `citation`, `image`, `embed`

## Custom Components

Create component + metadata, run autodiscovery:

```typescript
// src/ai/widget.tsx
export const Widget = ({ title, value }) => (
  <div><h3>{title}</h3><span>{value}</span></div>
);

export const metadata = {
  type: 'widget',
  description: 'Performance widget',
  schema: { /* JSON Schema */ },
  category: 'custom'
};
```

```bash
npx agentinterface discover  # Generates ai.json
```

Components automatically available to Python shaper LLM.

## Key Features

- **Universal**: Works with any agent/LLM combination
- **Extensible**: Add custom components via metadata
- **Interactive**: Bidirectional callbacks for user interaction
- **Compositional**: Multiple components with layout rules

## Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical design and implementation
- **[protocol.md](docs/protocol.md)** - Agent Interface Protocol (AIP) specification  
- **[artifacts.md](docs/artifacts.md)** - Comparison with Direct Artifacts

## API Reference

```python
# Python
ai(agent, llm, components=None, callback=None)
protocol(components=None)  # Generate LLM instructions  
shape(text, context, llm)  # Direct text → components
```

```typescript
// TypeScript
render(json, components?, onCallback?, metadata?)
```

## Development

```bash
npm install
npm run build          # compile ESM bundle + d.ts into dist/
npm run typecheck      # tsc --noEmit
npm run lint           # eslint
npm run test:unit      # Vitest suite
python -m pytest       # from ./python
```

Run `npm run build` before publishing so `package.json` entry points resolve to emitted files.

## License

MIT
