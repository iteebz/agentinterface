/**
 * AgentCanvas Example - Drop dead gorgeous infinite scroll
 */
import React, { useRef } from 'react';
import { AgentCanvas, AgentCanvasRef, formatLLM } from './src';

export function App() {
  const canvasRef = useRef<{ addResponse: (json: string) => void }>(null);

  // Add agent response to canvas
  const addAgentResponse = () => {
    const sampleResponse = JSON.stringify([
      {
        type: 'card',
        data: {
          title: 'Agent Response',
          content: 'Here is my analysis of your request...'
        }
      },
      {
        type: 'suggestions', 
        data: {
          suggestions: [
            { text: 'Tell me more about this' },
            { text: 'Show me an example' },
            { text: 'What are the alternatives?' }
          ]
        }
      }
    ]);

    // AgentCanvas has addResponse method exposed
    const canvas = document.querySelector('.agent-canvas') as any;
    if (canvas && canvas.addResponse) {
      canvas.addResponse(sampleResponse);
    }
  };

  // Handle user interactions with components
  const handleCallback = (event: any) => {
    console.log('User interaction:', formatLLM(event));
    // Send to agent, update conversation, etc.
  };

  return (
    <div className="h-screen flex flex-col">
      <header className="p-4 border-b">
        <h1 className="text-xl font-bold">AgentCanvas Example</h1>
        <button 
          onClick={addAgentResponse}
          className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
        >
          Add Agent Response
        </button>
      </header>
      
      <main className="flex-1">
        <AgentCanvas 
          onCallback={handleCallback}
          className="h-full"
        />
      </main>
    </div>
  );
}

export default App;