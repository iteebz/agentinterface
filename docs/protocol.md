# Agent Interface Protocol (AIP) v1.0.0

Specification for universal agent-to-UI communication systems.

## Overview

The Agent Interface Protocol defines standardized interfaces for:
- **Component selection** via shaper LLM reasoning
- **Component registry** format and discovery  
- **Callback architecture** for bidirectional communication
- **Composition rules** for multi-component layouts

## Shaper Protocol

### LLM Interface

```python
class LLM(Protocol):
    async def generate(self, prompt: str) -> str:
        """Generate component selection from agent text."""
```

### Prompt Generation

```python
def protocol(components: Optional[List[str]] = None) -> str:
    """Generate LLM instructions from component registry."""
    
    # Schema-driven component specifications  
    for comp_type, comp_info in registry["components"].items():
        schema = comp_info["schema"]
        required_props = [prop for prop, info in schema["properties"].items()
                         if not info.get("optional", False)]
        
        specs.append(f"{comp_type}: {description} (uses: {required_props})")
```

### Prompt Format

```
Available components:
- card: Generic card layout (uses: title, content)  
- table: Data display (uses: headers, rows)
- timeline: Event sequence (uses: events)

Composition patterns:
- Single: {"type": "card", "data": {"title": "Sales", "content": "..."}}
- Vertical: [component1, component2, component3]  
- Horizontal: [component1, [component2, component3]]
- Mixed: [card, [table, timeline], suggestions]

Return JSON array only.
```

**Function**: Provides LLM with component capabilities and composition patterns derived from actual schemas.

## Registry Protocol

### Schema Format

```typescript
interface ComponentRegistry {
  generated_at: string;          // ISO timestamp
  version: string;               // Registry version  
  total_components: number;      // Component count
  components: {
    [type: string]: {
      description: string;       // LLM-readable description
      schema: JSONSchema;        // Component props schema
      category: string;          // Grouping identifier
      file: string;              // Source file path
      source: string;            // Source package name
    }
  };
  sources: {
    [source: string]: string[]; // Source → component mapping
  }
}
```

### Component Metadata

```typescript
interface ComponentMetadata {
  type: string;                  // kebab-case identifier
  description: string;           // Human/LLM description
  schema: {
    type: 'object';
    properties: {
      [prop: string]: {
        type: string;
        optional?: boolean;
        enum?: string[];
        items?: any;
      }
    };
    required: string[];
  };
  category: string;              // layout, content, interactive, etc.
}
```

### Discovery Process

```javascript
// Autodiscovery implementation
1. Scan *.tsx files for metadata exports
2. Parse AST to extract metadata objects  
3. Validate schema compliance
4. Generate ai.json registry
5. Make available to protocol() function
```

**Output**: Single `ai.json` file containing all component specifications.

## Composition Protocol

### Layout Rules

```typescript
// Single component
ComponentJSON

// Vertical stack  
ComponentJSON[]

// Horizontal row
[ComponentJSON, ComponentJSON]

// Mixed composition
[
  ComponentJSON,                 // Vertical item
  [ComponentJSON, ComponentJSON], // Horizontal row  
  ComponentJSON                  // Vertical item
]
```

### Rendering Behavior

- **Arrays**: Vertical layout (`flex flex-col gap-6`)
- **Nested arrays**: Horizontal layout (`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`)
- **Components**: Recursive composition (infinite nesting)

### Component JSON Format

```typescript
interface ComponentJSON {
  type: string;                  // Maps to registry type
  data: Record<string, any>;     // Props for component
}

// Data can contain nested components
{
  "type": "card",
  "data": {
    "title": "Dashboard",
    "content": [
      {"type": "table", "data": {...}},
      {"type": "timeline", "data": {...}}
    ]
  }
}
```

## Callback Protocol

### Interface Definition

```python
@runtime_checkable  
class Callback(Protocol):
    async def await_interaction(self, timeout: int = 300) -> dict:
        """Wait for user interaction with component."""
    
    def endpoint(self) -> str:
        """Get callback endpoint URL."""
```

### Event Format

```typescript
interface CallbackEvent {
  action: string;                // click, select, submit, etc.
  data: any;                     // Action-specific payload
}

// Example events
{"action": "click", "data": {"componentId": "card-1"}}
{"action": "select", "data": {"value": "option-2", "text": "Sales"}}
```

### HTTP Implementation

```python
class Http(Callback):
    def __init__(self, id: str = None, port: int = 8228):
        self.id = id or str(uuid.uuid4())
        self._server = _get_shared_server(port)  # Shared server per port
        self._future = asyncio.Future()
        self._server.callbacks[self.id] = self._future
    
    async def await_interaction(self, timeout: int = 300) -> dict:
        try:
            return await asyncio.wait_for(self._future, timeout=timeout)
        finally:
            self._server.callbacks.pop(self.id, None)  # Self-cleanup
    
    def endpoint(self) -> str:
        host = os.getenv("AI_CALLBACK_HOST", "localhost")  
        return f"http://{host}:{self._server.port}/callback/{self.id}"
```

**Features**:
- **Shared servers**: Multiple callbacks per port
- **Self-cleanup**: Automatic removal after completion/timeout  
- **Configurable host**: `AI_CALLBACK_HOST` environment variable
- **Timeout management**: Abandoned callbacks cleaned after 600 seconds

## Agent Enhancement Protocol

### Wrapper Interface

```python
def ai(
    agent: Any,                    # Agent to enhance
    llm: LLM,                      # Shaper LLM  
    components: Optional[List[str]] = None,  # Component filter
    callback: Optional[Callback] = None,     # Callback instance
) -> Callable
```

### Agent Patterns

```python
# Any callable that returns text
Agent = Union[
    Callable[..., str],            # Sync function
    Callable[..., Awaitable[str]], # Async function  
    Callable[..., AsyncIterator[Any]] # Streaming function
]
```

### Response Types

```python
# Sync/Async agents → tuple
enhanced = ai(agent, llm)
text, components = await enhanced("query")

# Streaming agents → generator  
enhanced = ai(streaming_agent, llm)
async for event in enhanced("query"):
    if event["type"] == "component":
        components = event["data"]["components"]
        callback_url = event["data"].get("callback_url")
```

## Render Protocol

### Function Signature

```typescript
function render(
  agentJSON: string,                           // Component JSON string
  components?: Record<string, ComponentType>,  // Custom component map
  onCallback?: (event: CallbackEvent) => void, // Callback handler  
  metadata?: Record<string, any>               // Validation metadata
): React.ReactNode
```

### Component Resolution

1. **Custom components** (provided in components parameter)
2. **Built-in components** (DEFAULT_COMPONENTS registry)  
3. **Fallback rendering** (`<div>Unknown: {type}</div>`)

### Error Handling

```typescript
// Missing required props
if (metadata?.[type]?.schema?.required) {
  for (const requiredProp of metadata[type].schema.required) {
    if (!(requiredProp in processedData)) {
      return <div>Error: Missing required data for {type}</div>;
    }
  }
}
```

**Principle**: Fail visibly rather than silently.

## Error Handling

### Fail-Fast

```python
# Invalid JSON from LLM
raise ValueError(f"Invalid JSON from LLM: {e}")

# Missing callback response  
raise asyncio.TimeoutError()

# Invalid component schema
raise ValueError(f"Component {type} missing required metadata")
```

### Graceful Degradation

```python
# Malformed registry → markdown fallback
component_specs = ["markdown: Text content with formatting"]

# Missing custom components → built-in components
componentMap = components || DEFAULT_COMPONENTS

# Shaper failure → original text passthrough
return response if not component_json else component_json
```

## Version Compatibility

### Semantic Versioning

- **Major**: Breaking protocol changes (registry format, interface signatures)
- **Minor**: Additive features (new optional fields, additional protocols)
- **Patch**: Implementation fixes (bug fixes, performance improvements)

### Forward Compatibility

```typescript
// Optional fields preserve compatibility  
interface ComponentMetadata {
  type: string;           // Required
  description: string;    // Required  
  schema: JSONSchema;     // Required
  category: string;       // Required
  // Future optional fields added here
}
```

**Policy**: Required field additions constitute major version bump.

## Implementation Requirements

### Discovery Script
- Cross-platform Node.js compatibility
- AST parsing for accurate metadata extraction  
- Schema validation with clear error messages

### Python Package  
- Protocol-based abstractions with `@runtime_checkable`
- Fail-fast error handling with descriptive messages
- Optional dependencies for specific features (FastAPI for callbacks)

### TypeScript Package
- React 16.8+ compatibility (hooks support)
- ES modules with tree-shaking support
- Complete TypeScript definitions

---

**AIP v1.0.0** - Agent Interface Protocol specification