/**
 * Visual Test Suite - AgentCanvas in action
 * Open in browser to see if it actually works
 */
import React, { useRef, useEffect, useState } from 'react';
import { AgentCanvas, formatLLM } from '../src';

export function VisualTest() {
  return (
    <div className="p-4 space-y-8">
      <h1 className="text-2xl font-bold">AgentCanvas Visual Tests</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Test 1: Empty Canvas */}
        <TestCase title="Empty Canvas" description="Should show waiting message">
          <AgentCanvas className="h-64 border border-gray-300 rounded" />
        </TestCase>

        {/* Test 2: Single Response */}
        <TestCase title="Single Response" description="Should render one card">
          <SingleResponseTest />
        </TestCase>

        {/* Test 3: Multiple Responses */}
        <TestCase title="Multiple Responses" description="Should show infinite scroll">
          <MultipleResponsesTest />
        </TestCase>

        {/* Test 4: Interactive Components */}
        <TestCase title="Interactive Components" description="Should handle callbacks">
          <InteractiveTest />
        </TestCase>

        {/* Test 5: Complex Layout */}
        <TestCase title="Complex Layout" description="Should render arrays and nested components">
          <ComplexLayoutTest />
        </TestCase>

        {/* Test 6: Error Handling */}
        <TestCase title="Error Handling" description="Should handle invalid JSON gracefully">
          <ErrorHandlingTest />
        </TestCase>
      </div>
    </div>
  );
}

function TestCase({ title, description, children }: { 
  title: string; 
  description: string; 
  children: React.ReactNode; 
}) {
  return (
    <div className="space-y-2">
      <div>
        <h3 className="font-semibold">{title}</h3>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
      <div className="border rounded p-2">
        {children}
      </div>
    </div>
  );
}

function SingleResponseTest() {
  const [canvas, setCanvas] = useState<any>(null);

  useEffect(() => {
    if (canvas) {
      const response = JSON.stringify({
        type: 'card',
        data: {
          title: 'Test Card',
          content: 'This is a test response from an agent.'
        }
      });
      canvas.addResponse(response);
    }
  }, [canvas]);

  return (
    <AgentCanvas 
      ref={setCanvas}
      className="h-64 border border-gray-300 rounded" 
    />
  );
}

function MultipleResponsesTest() {
  const [canvas, setCanvas] = useState<any>(null);

  useEffect(() => {
    if (canvas) {
      // Add responses with delays
      setTimeout(() => {
        canvas.addResponse(JSON.stringify({
          type: 'markdown',
          data: { content: '# First Response\nThis is the first agent response.' }
        }));
      }, 100);

      setTimeout(() => {
        canvas.addResponse(JSON.stringify({
          type: 'card',
          data: {
            title: 'Second Response',
            content: 'This should appear below the first response.'
          }
        }));
      }, 500);

      setTimeout(() => {
        canvas.addResponse(JSON.stringify([
          {
            type: 'table',
            data: {
              title: 'Data Table',
              attributes: [
                { key: 'name', label: 'Name' },
                { key: 'value', label: 'Value' }
              ],
              items: [
                { id: '1', name: 'Test 1', attributes: { name: 'Alpha', value: '100' } },
                { id: '2', name: 'Test 2', attributes: { name: 'Beta', value: '200' } }
              ]
            }
          }
        ]));
      }, 1000);
    }
  }, [canvas]);

  return (
    <AgentCanvas 
      ref={setCanvas}
      className="h-64 border border-gray-300 rounded overflow-y-auto" 
    />
  );
}

function InteractiveTest() {
  const [canvas, setCanvas] = useState<any>(null);
  const [lastEvent, setLastEvent] = useState<string>('No interactions yet');

  const handleCallback = (event: any) => {
    const formatted = formatLLM(event);
    setLastEvent(formatted);
    console.log('Callback:', formatted);
  };

  useEffect(() => {
    if (canvas) {
      const response = JSON.stringify({
        type: 'suggestions',
        data: {
          title: 'Try clicking these:',
          suggestions: [
            { text: 'Option A', id: 'a' },
            { text: 'Option B', id: 'b' },
            { text: 'Option C', id: 'c' }
          ]
        }
      });
      canvas.addResponse(response);
    }
  }, [canvas]);

  return (
    <div className="space-y-2">
      <div className="text-sm text-gray-600">
        Last interaction: <span className="font-mono">{lastEvent}</span>
      </div>
      <AgentCanvas 
        ref={setCanvas}
        onCallback={handleCallback}
        className="h-64 border border-gray-300 rounded" 
      />
    </div>
  );
}

function ComplexLayoutTest() {
  const [canvas, setCanvas] = useState<any>(null);

  useEffect(() => {
    if (canvas) {
      // Complex layout with arrays (horizontal) and nested components
      const response = JSON.stringify([
        {
          type: 'markdown',
          data: { content: '## Complex Layout Test' }
        },
        [
          {
            type: 'card',
            data: {
              title: 'Left Card',
              content: 'This should be on the left'
            }
          },
          {
            type: 'card',
            data: {
              title: 'Right Card', 
              content: 'This should be on the right'
            }
          }
        ],
        {
          type: 'timeline',
          data: {
            events: [
              {
                date: '2024-01-01',
                title: 'Event 1',
                description: 'First event description'
              },
              {
                date: '2024-01-02', 
                title: 'Event 2',
                description: 'Second event description'
              }
            ]
          }
        }
      ]);
      canvas.addResponse(response);
    }
  }, [canvas]);

  return (
    <AgentCanvas 
      ref={setCanvas}
      className="h-64 border border-gray-300 rounded" 
    />
  );
}

function ErrorHandlingTest() {
  const [canvas, setCanvas] = useState<any>(null);

  useEffect(() => {
    if (canvas) {
      // Test invalid JSON
      canvas.addResponse('invalid json');
      
      // Test unknown component type
      setTimeout(() => {
        canvas.addResponse(JSON.stringify({
          type: 'nonexistent',
          data: { test: 'data' }
        }));
      }, 100);
      
      // Test valid component after errors
      setTimeout(() => {
        canvas.addResponse(JSON.stringify({
          type: 'card',
          data: {
            title: 'Recovery Test',
            content: 'This should work after the errors'
          }
        }));
      }, 200);
    }
  }, [canvas]);

  return (
    <AgentCanvas 
      ref={setCanvas}
      className="h-64 border border-gray-300 rounded" 
    />
  );
}

export default VisualTest;