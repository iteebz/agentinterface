/**
 * AgentInterface - Agent JSON → React components
 */


// AgentCanvas - infinite scroll container for agent responses
export { AgentCanvas } from './canvas';
export type { AgentCanvasRef } from './canvas';

// Core rendering utilities
export { render } from './renderer';

// All AI components
export { Accordion } from './ai/accordion';
export { Card } from './ai/card';
export { Embed } from './ai/embed';
export { Image } from './ai/image';
export { Markdown } from './ai/markdown';
export { Citation } from './ai/citation';
export { Suggestions } from './ai/suggestions';
export { Table } from './ai/table';
export { Tabs } from './ai/tabs';
export { Timeline } from './ai/timeline';

// Types and utilities
export type { 
  CallbackEvent, 
  ComponentData, 
  ComponentArray, 
  ComponentMetadata,
  AgentResponse,
  AgentCanvasProps 
} from './types';
export { formatLLM } from './types';
