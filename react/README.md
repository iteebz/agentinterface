# AgentInterface React

React renderer for AgentInterface. Transforms component JSON into interactive UIs with 10 built-in components and custom component support.

```bash
npm install agentinterface
```

## Quick Start

```tsx
import { render } from 'agentinterface';

function Dashboard({ componentJSON }) {
  return <div>{render(componentJSON)}</div>;
}
```

## Built-in Components

`card` `table` `timeline` `accordion` `tabs` `markdown` `image` `embed` `citation` `suggestions`

## Array Composition

Nested arrays for layout:

```python
# Vertical stack
[card1, card2, card3]

# Horizontal grid
[[card1, card2, card3]]

# Mixed
[
  card1,              # Full width
  [card2, card3],     # Side by side
  table1              # Full width
]
```

## Custom Components

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

Discover and use:

```bash
npx agentinterface discover
```

```tsx
import { render } from 'agentinterface';
import { Metric } from './ai/metric';

render(componentJSON, { metric: Metric })
```

## Bidirectional Callbacks

```tsx
render(componentJSON, {}, ({ type, data }) => {
  if (type === 'interaction') {
    // Handle user interaction
  }
});
```

## API

```tsx
render(json, components?, onCallback?)
```

## Development

```bash
npm install
npm test
npm run build
npm run lint
```

## License

MIT
