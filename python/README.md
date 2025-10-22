# AgentInterface

**Agents shape UI. Not templates.**

Agent GUIs without ceremony.

```bash
pip install agentinterface
```

## Pattern

```
Agent text → Shaper LLM → Component JSON → React UI
```

Wrap any agent. Any LLM selects components. React renders UI.

## Usage

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

## LLM Providers

```python
# String providers (defaults: gpt-4.1-mini, gemini-2.5-flash, claude-4.5-sonnet-latest)
ai(agent, llm="openai")
ai(agent, llm="gemini")
ai(agent, llm="anthropic")

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

## Composition

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

Nested arrays = horizontal. Arrays = vertical.

## Bidirectional Callbacks

```python
from agentinterface.callback import Http

callback = Http()
enhanced = ai(agent, llm="gemini", callback=callback)

async for event in enhanced("Show sales dashboard"):
    if event["type"] == "component":
        components = event["data"]["components"]
        
        # User clicks → callback receives interaction
        interaction = await callback.await_interaction(timeout=300)
        
        # Agent continues based on interaction
```

Components talk back to agent. Conversational UI.

## Custom Components

Create React component with metadata:

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

Component automatically available to shaper LLM.

## Built-in Components

10 components: `card` `table` `timeline` `accordion` `tabs` `markdown` `image` `embed` `citation` `suggestions`

## API

```python
ai(agent, llm, components=None, callback=None, timeout=300)
protocol(components=None)
shape(text, context, llm)
```

## Docs

Full documentation: [github.com/iteebz/agentinterface](https://github.com/iteebz/agentinterface)

## License

MIT