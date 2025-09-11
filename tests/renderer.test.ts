/**
 * Core renderer tests
 */
import React from 'react';

// Mock render function for Node.js testing
function render(
  agentJSON: string,
  components: Record<string, (props: any) => any>,
  metadata?: Record<string, any>
): any {
  function processData(data: any): any {
    if (data && typeof data === 'object' && data.type) {
      return renderItem(data, 0);
    }
    if (Array.isArray(data)) {
      return data.map((item, i) => processData(item));
    }
    return data;
  }

  function renderItem(item: any, key: number): any {
    if (Array.isArray(item)) {
      return {
        key,
        props: {
          className: "flex gap-4",
          children: item.map((subItem, i) => renderItem(subItem, i))
        }
      };
    }
    
    const { type, data } = item;
    const processedData = Object.fromEntries(
      Object.entries(data || {}).map(([k, v]) => [k, processData(v)])
    );
    
    if (metadata?.[type]?.schema?.required) {
      for (const requiredProp of metadata[type].schema.required) {
        if (!(requiredProp in processedData)) {
          return {
            key,
            props: {
              children: `Error: Missing required data for ${type}`
            }
          };
        }
      }
    }
    
    const Component = components[type];
    if (!Component) {
      return {
        key,
        props: {
          children: `Unknown: ${type}`
        }
      };
    }
    
    return {
      key,
      ...Component({...processedData})
    };
  }

  const parsed = JSON.parse(agentJSON);
  
  if (Array.isArray(parsed)) {
    return {
      props: {
        className: "flex flex-col gap-4",
        children: parsed.map((item, i) => renderItem(item, i))
      }
    };
  }
  
  return renderItem(parsed, 0);
}

const mockComponents = {
  'card': (props: any) => props,
  'table': (props: any) => props,
};

const mockMetadata = {
  'card': {
    schema: {
      required: ['title']
    }
  }
};

console.log('🧪 Testing renderer...');

// Test 1: Schema validation
console.log('1. Testing schema validation...');
const invalidComponent = { type: 'card', data: { content: 'Missing title' } };
const result1 = render(JSON.stringify(invalidComponent), mockComponents, mockMetadata);

if (result1?.props?.children?.includes('Missing required data for card')) {
  console.log('   ✅ Schema validation correctly identified missing props');
} else {
  console.error('   ❌ Schema validation failed');
  process.exit(1);
}

// Test 2: Nested component resolution
console.log('2. Testing nested component resolution...');
const nestedComponent = { 
  type: 'card', 
  data: { 
    title: 'Card Title',
    content: { type: 'table', data: { rows: ['data'] } }
  } 
};

const result2 = render(JSON.stringify(nestedComponent), mockComponents, mockMetadata);

if (result2?.title === 'Card Title' && result2?.content?.rows?.[0] === 'data') {
  console.log('   ✅ Nested component correctly resolved');
} else {
  console.error('   ❌ Nested component test failed');
  process.exit(1);
}

// Test 3: Array composition
console.log('3. Testing array composition...');
const arrayComponents = [
  { type: 'card', data: { title: 'Card 1' } },
  { type: 'card', data: { title: 'Card 2' } }
];

const result3 = render(JSON.stringify(arrayComponents), mockComponents, mockMetadata);

if (result3?.props?.className === 'flex flex-col gap-4' && Array.isArray(result3?.props?.children)) {
  console.log('   ✅ Array composition correctly rendered vertical stack');
} else {
  console.error('   ❌ Array composition test failed');
  process.exit(1);
}

console.log('\n🎉 All renderer tests passed!');