# Component Comparison

## Direct Artifacts

Manual component selection:

```
User: "Write a React component"
Claude: [Automatically renders in code artifact container]
```

**Limitations:** Single source. Manual selection.

## AgentInterface

Universal component selection:

```python
# Any agent becomes artifact-capable
agent = ai(openai_agent, llm)
result = await agent("Write a React component")
# Returns: (text, [{"type": "code", "data": {"language": "javascript", "content": "..."}}])
```

**Advantages:** Universal. Systematic. Extensible.

## Technical Comparison

| Feature | Direct Artifacts | AgentInterface |
|---------|----------------|----------------|
| Agents | Limited | Universal |
| Components | Fixed | Extensible |
| Selection | Manual | LLM-driven |
| Composition | Single | Nested |
| Callbacks | Limited | Built-in |

## Key Differences

**Direct artifacts:** Specific agent, fixed component types

**AgentInterface:** 
- Universal agent support
- Extensible component system
- LLM-driven selection
- Developer-controlled integration

## Positioning

AgentInterface generalizes component selection to any agent, expanding beyond fixed containers to a complete component ecosystem.

**Universal. Extensible. Zero ceremony.**