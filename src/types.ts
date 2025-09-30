export interface ComponentMetadata {
  type: string;
  description: string;
  schema: {
    type: "object";
    properties: Record<
      string,
      {
        type: string;
        optional?: boolean;
        enum?: string[];
        items?: any;
      }
    >;
    required: string[];
  };
  category: string;
}

export interface ComponentJSON {
  type: string;
  data: Record<string, any>;
}

export type ComponentArray = ComponentJSON[];

export interface CallbackEvent {
  type: "click" | "change" | "select" | "toggle";
  component: string;
  data: Record<string, any>;
}

export interface AgentResponse {
  id: string;
  timestamp: number;
  content: ComponentJSON | ComponentArray;
}

export interface AgentCanvasProps {
  onCallback?: (event: CallbackEvent) => void;
  className?: string;
  maxResponses?: number;
}

export function formatLLM(event: CallbackEvent): string {
  const actionMap: Record<CallbackEvent["type"], string> = {
    click: "clicked",
    change: "changed",
    select: "selected",
    toggle: "toggled",
  };
  const action = actionMap[event.type] ?? event.type;
  const detail =
    event.data.title ||
    event.data.text ||
    event.data.id ||
    event.data.label ||
    "";
  return `User ${action} ${event.component}${detail ? ": " + detail : ""}`;
}
