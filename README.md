# AgentInterface

**Agents shape UI. Not templates.**

Agent GUIs without ceremony. LLM selects components. React renders. Infinite composition.

```bash
npm install agentinterface  # React renderer
pip install agentinterface  # Python agent wrapper
```

## Pattern

```
Agent text → Shaper LLM → Component JSON → React UI
```

## SDK Documentation

- **[React SDK](./react/README.md)** - Component rendering and composition
- **[Python SDK](./python/README.md)** - Agent wrapping and LLM integration

## Development

```bash
just install   # Install both SDKs
just ci        # Run linting, formatting, tests
just publish   # Publish to npm and PyPI
```

See [react/README.md](./react/README.md) and [python/README.md](./python/README.md) for SDK-specific development.

## License

MIT
