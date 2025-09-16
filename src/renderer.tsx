import React from 'react';
import type { ComponentType } from 'react';
import { CallbackEvent } from './types';
import { Accordion } from './ai/accordion';
import { Card } from './ai/card';
import { Citation } from './ai/citation';
import { Embed } from './ai/embed';
import { Image } from './ai/image';
import { Markdown } from './ai/markdown';
import { Suggestions } from './ai/suggestions';
import { Table } from './ai/table';
import { Tabs } from './ai/tabs';
import { Timeline } from './ai/timeline';

// Default component registry
const DEFAULT_COMPONENTS = {
  accordion: Accordion,
  card: Card,
  citation: Citation,
  embed: Embed,
  image: Image,
  markdown: Markdown,
  suggestions: Suggestions,
  table: Table,
  tabs: Tabs,
  timeline: Timeline,
};

// Core component rendering logic
export function render(
  agentJSON: string,
  components?: Record<string, React.ComponentType<any>>,
  onCallback?: (event: CallbackEvent) => void,
  metadata?: Record<string, any>
): React.ReactNode {
  
  // Load autodiscovered components if none provided
  const componentMap: Record<string, ComponentType<any>> = {
    ...DEFAULT_COMPONENTS,
    ...(components ?? {}),
  };
  
  function processData(data: any): any {
    if (data && typeof data === 'object' && data.type) {
      return renderItem(data, 0);
    }
    if (Array.isArray(data)) {
      return data.map((item, i) => processData(item));
    }
    return data;
  }

  function renderItem(item: any, key: number): React.ReactNode {
    if (Array.isArray(item)) {
      return (
        <div key={key} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 w-full">
          {item.map((subItem, i) => renderItem(subItem, i))}
        </div>
      );
    }
    
    const { type, data } = item;
    
    const processedData = Object.fromEntries(
      Object.entries(data || {}).map(([k, v]) => [k, processData(v)])
    );
    
    if (metadata?.[type]?.schema?.required) {
      for (const requiredProp of metadata[type].schema.required) {
        if (!(requiredProp in processedData)) {
          return <div key={key}>Error: Missing required data for {type}</div>;
        }
      }
    }
    
    const Component = componentMap[type];
    if (!Component) {
      return <div key={key}>Unknown: {type}</div>;
    }
    
    // Pass callback to components
    return <Component key={key} {...processedData} onCallback={onCallback} />;
  }

  const parsed = JSON.parse(agentJSON);
  return Array.isArray(parsed) 
    ? <div className="space-y-6">{parsed.map((item, i) => renderItem(item, i))}</div>
    : renderItem(parsed, 0);
}
