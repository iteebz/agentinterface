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

export function formatLLM(event: CallbackEvent): string {
  const action = event.type === 'toggle' ? 'toggled' : `${event.type}ed`;
  const detail = event.data.title || event.data.text || event.data.id || event.data.label || '';
  return `User ${action} ${event.component}${detail ? ': ' + detail : ''}`;
}