# AgentInterface Python

Agents choose components. Universal agent wrapper.

```python
from agentinterface import ai

# Universal wrapper
agent = ai(your_agent, llm)
result = await agent("Show sales data")
# Returns: (text, components)
```

## Installation

```bash
pip install agentinterface
```

## Usage

Works with any agent framework. Agent generates response, shaper LLM selects optimal UI components, renderer creates interactive interface.