# Custom Components

Zero ceremony custom components for AgentInterface.

## Installation

**Frontend:**
```bash
npm install agentinterface
```

**Backend:**
```bash
pip install agentinterface
```

## Usage

### 1. Create Component

**`src/components/ai/my-widget.tsx`**
```tsx
import React from 'react';

interface MyWidgetProps {
  title: string;
  value: number;
}

export function MyWidget({ title, value }: MyWidgetProps) {
  return (
    <div className="p-4 border rounded">
      <h3>{title}</h3>
      <p>Value: {value}</p>
    </div>
  );
}

export const metadata = {
  type: 'my-widget',
  description: 'Custom widget with title and value',
  schema: {
    type: 'object',
    properties: {
      title: { type: 'string' },
      value: { type: 'number' }
    },
    required: ['title', 'value']
  },
  category: 'custom'
};
```

### 2. Discover Components

```bash
npm run discover
```

This generates:
- `ai.json` - Component registry for LLM
- `ai.tsx` - Auto-generated wrapper with component imports

### 3. Use in Python

```python
from agentinterface import ai, protocol

def my_agent(query: str):
    return f"Custom widget response: {query}"

# Protocol automatically includes discovered components
instructions = protocol()

# AI wrapper automatically works with custom components
smart_agent = ai(my_agent, llm, interactive=True)

# Agent can now generate my-widget components
result = smart_agent("Show me a performance widget")
```

### 4. Render in Frontend

```tsx
import { render } from 'agentinterface';

// Renderer automatically includes discovered components
function MyApp() {
  const agentOutput = `[{
    "type": "my-widget", 
    "data": {"title": "Performance", "value": 95}
  }]`;
  
  // The ai.tsx auto-generated wrapper exports render()
  return <div>{render(agentOutput)}</div>;
}
```

## Component Structure

**Required exports:**
- Component function (PascalCase name)  
- `metadata` object with type, description, schema, category

**Schema properties:**
- `type`: Component identifier (kebab-case)
- `description`: What the component does
- `schema`: JSON Schema for props validation
- `category`: Grouping (layout, content, interactive, etc.)

## Workflow

1. **Write component** → Export component + metadata
2. **Run discover** → Generates registries  
3. **Everything works** → LLM knows it, renderer renders it

Components are automatically available to both Python backend and TypeScript frontend.

## Example: Chart Component

```tsx
// src/components/ai/chart.tsx
export function Chart({ data, type }: ChartProps) { /* ... */ }

export const metadata = {
  type: 'chart',
  description: 'Data visualization chart',
  schema: {
    type: 'object',
    properties: {
      data: { type: 'array' },
      type: { type: 'string', enum: ['bar', 'line', 'pie'] }
    },
    required: ['data', 'type']
  },
  category: 'visualization'
};
```

```bash
npm run discover
```

```python
# Backend automatically knows about chart component
agent_response = smart_agent("Show sales data as bar chart")
# Can generate: {"type": "chart", "data": {...}, "type": "bar"}
```

```tsx
// Frontend automatically renders chart component
render(agent_response) // Auto-discovered components
```

**Single source of truth. Zero ceremony. Just works.**