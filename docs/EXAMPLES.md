# Examples

## Text to Components

Direct component transformation:

```python
from agentinterface import shape, protocol
from your_llm import LLM

llm = LLM()
agent_response = "Q3 sales increased 15%. Key metrics: Revenue $2M, Users 10K, Churn 2%."

# Transform to components  
shaped = await shape(
    response=agent_response,
    context={"query": "Show Q3 results", "domain": "business"},
    llm=llm
)

# Returns component JSON:
# [
#   {"type": "markdown", "data": {"content": "## Q3 Results\nSales increased 15%"}},
#   {"type": "table", "data": {"headers": ["Metric", "Value"], "rows": [["Revenue", "$2M"], ["Users", "10K"]]}}
# ]
```

## Agent Integration

Full bidirectional workflow:

```python
from agentinterface import ai

# Your agent (any callable)
async def agent(query: str) -> str:
    return f"Sales analysis for: {query}"

# Core integration pattern
agent = ai(agent, llm=your_llm)
async for event in agent("Show Q3 dashboard"):
    if event["type"] == "component":
        # Component rendering
        render(event["data"]["components"])
    else:
        # Passthrough
        yield event
```

## Registry Protocol

Generate component instructions:

```python
from agentinterface import protocol

# Get instructions for specific components
instructions = protocol(["table", "card", "timeline"])

# Or use all available components
instructions = protocol()  # Auto-discovers from ai.json
```

## Component Rendering

Render JSON in React:

```typescript
import { render } from 'agentinterface';

const componentData = [
  {"type": "card", "data": {"title": "Results"}},
  [
    {"type": "table", "data": {"headers": ["Metric", "Value"], "rows": [["Speed", "95%"]]}},
    {"type": "timeline", "data": {"events": [{"date": "2024", "title": "Launch"}]}}
  ]
];

function Dashboard() {
  return <div>{render(JSON.stringify(componentData), components)}</div>;
}
```

## Custom Components

Add specialized components:

```typescript
// components/Portfolio.tsx
export const metadata = {
  type: 'portfolio',
  description: 'Project showcase with skills',
  schema: {
    type: 'object',
    properties: {
      projects: { type: 'array' },
      skills: { type: 'array' }
    }
  }
};

export function Portfolio({ projects, skills }) {
  return (
    <div>
      {projects.map(p => <div key={p.name}>{p.name}</div>)}
    </div>
  );
}
```

```bash
# Discover and register
npx agentinterface discover
# Portfolio automatically available to shaper LLM
```

## Error Handling

```python
from agentinterface import shape

try:
    shaped = await shape(response, context, llm)
except Exception:
    # Fallback to text
    shaped = [{"type": "markdown", "data": {"content": response}}]
```

## Compatibility

Works with any pattern:

```python
# Callable agents
agent = lambda q: f"Analysis: {q}"
agent = ai(agent, llm)
result = await agent("Query")

# Class-based agents  
class MyAgent:
    async def run(self, query):
        return f"Result: {query}"

agent = ai(MyAgent(), llm)
result = await agent("Query")

# Function agents
async def agent(query):
    return await do_research(query)
    
agent = ai(agent, llm)
result = await agent("Query")
```