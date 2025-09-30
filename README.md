# AgentInterface

Agents choose UI components. Zero ceremony.

```bash
npm install agentinterface  # React renderer + 10 components
pip install agentinterface  # Python agent wrapper
```

## Pattern

```
Agent text → Shaper LLM → Component JSON → React UI
```

Any agent. Any LLM. Any component.

## Python: Enhance Agents

```python
from agentinterface import ai

def sales_agent(query: str) -> str:
    return "Q3 revenue: $2M, up 15%. Users: 10K."

enhanced = ai(sales_agent, llm="gemini")
text, components = await enhanced("Show Q3 dashboard")

# Returns:
# text: "Q3 revenue: $2M, up 15%. Users: 10K."
# components: [{"type": "card", "data": {"title": "Q3 Revenue", "value": "$2M"}}]
```

Works with sync, async, streaming agents.

## React: Render Components

```tsx
import { render } from 'agentinterface';

function Dashboard({ componentJSON }) {
  return <div>{render(componentJSON)}</div>;
}
```

10 built-in components: `card` `table` `timeline` `accordion` `tabs` `markdown` `image` `embed` `citation` `suggestions`

## Array Composition

```python
# Vertical stack
[card1, card2, card3]

# Horizontal grid
[[card1, card2, card3]]

# Mixed layout
[
  card1,              # Full width
  [card2, card3],     # Side by side
  table1              # Full width
]
```

Nested arrays = horizontal. Arrays = vertical. Infinite nesting.

## Custom Components

Create component with metadata:

```tsx
// src/ai/metric.tsx
export const Metric = ({ label, value, change }) => (
  <div>
    <span>{label}</span>
    <strong>{value}</strong>
    <span>{change}</span>
  </div>
);

export const metadata = {
  type: 'metric',
  description: 'Key performance metric with change indicator',
  schema: {
    type: 'object',
    properties: {
      label: { type: 'string' },
      value: { type: 'string' },
      change: { type: 'string', optional: true }
    },
    required: ['label', 'value']
  },
  category: 'content'
};
```

Run autodiscovery:

```bash
npx agentinterface discover
```

Component automatically available to shaper LLM. Import and pass to renderer:

```tsx
import { render } from 'agentinterface';
import { Metric } from './ai/metric';

render(componentJSON, { metric: Metric })
```

## Bidirectional Callbacks

```python
from agentinterface import ai
from agentinterface.callback import Http

callback = Http()
enhanced = ai(agent, llm="gemini", callback=callback)

async for event in enhanced("Show sales dashboard"):
    if event["type"] == "component":
        components = event["data"]["components"]
        callback_url = event["data"]["callback_url"]
        
        # User clicks → callback receives interaction
        interaction = await callback.await_interaction(timeout=300)
        
        # Agent continues based on interaction
```

Components send data back to agent. Conversational UI.

## API

**Python:**
```python
ai(agent, llm, components=None, callback=None, timeout=300)
protocol(components=None)
shape(text, context, llm)
```

**TypeScript:**
```tsx
render(json, components?, onCallback?)
```

**LLM Providers:**
```python
# String providers (default models)
ai(agent, llm="openai")     # gpt-4.1-mini
ai(agent, llm="gemini")     # gemini-2.5-flash
ai(agent, llm="anthropic")  # claude-4.5-sonnet-latest

# Custom models
from agentinterface.llms import OpenAI, Gemini, Anthropic
ai(agent, llm=OpenAI(model="gpt-4o"))
ai(agent, llm=Gemini(model="gemini-pro"))

# Custom LLM
from agentinterface.llms import LLM

class CustomLLM(LLM):
    async def generate(self, prompt: str) -> str:
        ...

ai(agent, llm=CustomLLM())
```

## Docs

- [**architecture.md**](docs/architecture.md) - System design
- [**components.md**](docs/components.md) - Component reference
- [**composition.md**](docs/composition.md) - Array composition
- [**callbacks.md**](docs/callbacks.md) - Bidirectional communication

## Development

```bash
# TypeScript
npm install
npm test
npm run build

# Python
cd python
poetry install
poetry run pytest
```

## License

MIT