export interface ComponentMetadata {
  type: string;
  description: string;
  schema: {
    type: string;
    properties: Record<string, any>;
    required: string[];
  };
  category: string;
}

export interface ComponentData {
  type: string;
  data: Record<string, any>;
}

export type ComponentArray = ComponentData[];

export interface CallbackEvent {
  type: 'click' | 'change' | 'select' | 'toggle';
  component: string;
  data: Record<string, any>;
}

export interface AgentResponse {
  id: string;
  timestamp: number;
  content: ComponentData | ComponentArray;
}

export interface AgentCanvasProps {
  onCallback?: (event: CallbackEvent) => void;
  className?: string;
  maxResponses?: number;
}

export function formatLLM(event: CallbackEvent): string {
  const actionMap: Record<CallbackEvent['type'], string> = {
    click: 'clicked',
    change: 'changed',
    select: 'selected',
    toggle: 'toggled',
  };
  const action = actionMap[event.type] ?? event.type;
  const detail =
    event.data.title ||
    event.data.text ||
    event.data.id ||
    event.data.label ||
    '';
  return `User ${action} ${event.component}${detail ? ': ' + detail : ''}`;
}
