# Callbacks

Bidirectional agent-UI communication.

## Protocol

```python
class Callback(Protocol):
    async def await_interaction(self, timeout: int = 300) -> dict:
        """Wait for user interaction."""
    
    def endpoint(self) -> str:
        """Get callback URL."""
```

Two methods. Any transport.

## Usage

```python
from agentinterface import ai
from agentinterface.callback import Http

callback = Http(port=8228)
enhanced = ai(agent, llm="gemini", callback=callback)

async for event in enhanced("Show sales dashboard"):
    if event["type"] == "component":
        components = event["data"]["components"]
        callback_url = event["data"]["callback_url"]
        
        interaction = await callback.await_interaction(timeout=300)
```

Agent streams → Components render → User clicks → Agent continues.

## Component Integration

```tsx
import { render } from 'agentinterface';

const handleCallback = (event) => {
  fetch(callbackURL, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(event)
  });
};

<div>{render(componentJSON, undefined, handleCallback)}</div>
```

User clicks → `onCallback` fires → POST → Agent receives interaction.

## Conversation Loop

```python
callback = Http()
enhanced = ai(agent, llm="gemini", callback=callback)

async for event in enhanced("Show sales"):
    if event["type"] == "component":
        render_ui(components, event["data"]["callback_url"])
        interaction = await callback.await_interaction()
        # Agent automatically continues with interaction context
```

Infinite loop: Agent → Components → User → Agent...

## Event Format

```python
{
  "action": "click",
  "data": {"button": "Deep Dive", "id": "card-123"}
}
```

Common actions: `click`, `select`, `submit`, `change`.

## Custom Transport

```python
class WebSocketCallback(Callback):
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.future = asyncio.Future()
    
    async def await_interaction(self, timeout: int = 300) -> dict:
        async with websockets.connect(self.ws_url) as ws:
            message = await asyncio.wait_for(ws.recv(), timeout=timeout)
            return json.loads(message)
    
    def endpoint(self) -> str:
        return self.ws_url

callback = WebSocketCallback("wss://example.com/callback")
enhanced = ai(agent, llm="gemini", callback=callback)
```

## Shared Server Pattern

```python
callback1 = Http(id="user-123", port=8228)
callback2 = Http(id="user-456", port=8228)
callback3 = Http(id="user-789", port=8228)
```

Multiple callbacks share one server. Routed by ID: `/callback/{id}`.

## Cleanup

Automatic cleanup on success/timeout. Abandoned callbacks cleaned after 600s. Zero memory leaks.

## Environment

```bash
AI_CALLBACK_HOST=myserver.com  # Default: localhost
```