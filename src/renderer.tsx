/**
 * Renderer for AgentInterface
 * Converts agent JSON to React components with composition logic
 */

import React from 'react';

/**
 * Render agent JSON into React components
 */
export function render(
  agentJSON: string,
  components: Record<string, React.ComponentType<any>>,
  metadata?: Record<string, any>
): React.ReactNode {
  
  function processData(data: any): any {
    if (data && typeof data === 'object' && data.type) {
      return renderItem(data, 0); // Nested component
    }
    if (Array.isArray(data)) {
      return data.map((item, i) => processData(item)); // Nested arrays
    }
    return data; // Regular data passthrough
  }

  function renderItem(item: any, key: number): React.ReactNode {
    if (Array.isArray(item)) {
      // Horizontal stack
      return (
        <div key={key} className="flex gap-4">
          {item.map((subItem, i) => renderItem(subItem, i))}
        </div>
      );
    }
    
    // Single component
    const { type, data } = item;
    
    // Process all data props for nesting
    const processedData = Object.fromEntries(
      Object.entries(data || {}).map(([k, v]) => [k, processData(v)])
    );
    
    // Schema-aware validation: ensure required props exist
    if (metadata?.[type]?.schema?.required) {
      for (const requiredProp of metadata[type].schema.required) {
        if (!(requiredProp in processedData)) {
          console.warn(`Missing required prop '${requiredProp}' for component '${type}'`);
          return <div key={key}>Error: Missing required data for {type}</div>;
        }
      }
    }
    
    const Component = components[type];
    if (!Component) {
      return <div key={key}>Unknown: {type}</div>;
    }
    
    // Type-safe component props spreading
    return <Component key={key} {...processedData} />;
  }

  const parsed = JSON.parse(agentJSON);
  
  if (Array.isArray(parsed)) {
    // Vertical stack
    return (
      <div className="flex flex-col gap-4">
        {parsed.map((item, i) => renderItem(item, i))}
      </div>
    );
  }
  
  // Single component (backwards compatible)
  return renderItem(parsed, 0);
}

