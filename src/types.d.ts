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