import React from 'react';
export function render(
  agentJSON: string,
  components: Record<string, React.ComponentType<any>>,
  metadata?: Record<string, any>
): React.ReactNode {
  
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
        <div key={key} className="flex gap-4">
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
    
    const Component = components[type];
    if (!Component) {
      return <div key={key}>Unknown: {type}</div>;
    }
    
    return <Component key={key} {...processedData} />;
  }

  const parsed = JSON.parse(agentJSON);
  return Array.isArray(parsed) 
    ? <div className="flex flex-col gap-4">{parsed.map((item, i) => renderItem(item, i))}</div>
    : renderItem(parsed, 0);
}

