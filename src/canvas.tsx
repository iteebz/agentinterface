import React, {
  useState,
  useCallback,
  useRef,
  useImperativeHandle,
  forwardRef,
} from "react";
import { AgentResponse, AgentCanvasProps, CallbackEvent } from "./types";
import { render } from "./renderer";

const AUTO_SCROLL_DELAY_MS = 50;

export interface AgentCanvasRef {
  addResponse: (agentJSON: string) => void;
}

export const AgentCanvas = forwardRef<AgentCanvasRef, AgentCanvasProps>(
  ({ onCallback, className = "", maxResponses = 100 }, ref) => {
    const [responses, setResponses] = useState<AgentResponse[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    const addResponse = useCallback(
      (agentJSON: string) => {
        try {
          const content = JSON.parse(agentJSON);
          const response: AgentResponse = {
            id: `response_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`,
            timestamp: Date.now(),
            content,
          };

          setResponses((prev) => {
            const updated = [...prev, response];
            return updated.length > maxResponses
              ? updated.slice(-maxResponses)
              : updated;
          });

          setTimeout(() => {
            if (scrollRef.current) {
              scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
            }
          }, AUTO_SCROLL_DELAY_MS);
        } catch (error) {
          throw new Error(`Invalid JSON response: ${error}`);
        }
      },
      [maxResponses],
    );

    const handleCallback = useCallback(
      (event: CallbackEvent) => {
        onCallback?.(event);
      },
      [onCallback],
    );

    useImperativeHandle(ref, () => ({ addResponse }), [addResponse]);

    return (
      <div
        ref={scrollRef}
        className={`agent-canvas overflow-y-auto h-full bg-gray-50 dark:bg-gray-900 ${className}`}
        style={{ scrollBehavior: "smooth" }}
      >
        <div className="max-w-4xl mx-auto space-y-8 p-6">
          {responses.map((response) => (
            <div key={response.id} className="response-container">
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-3 font-mono">
                {new Date(response.timestamp).toLocaleString()}
              </div>
              <div className="response-content">
                {render(
                  JSON.stringify(response.content),
                  undefined,
                  handleCallback,
                )}
              </div>
            </div>
          ))}
          {responses.length === 0 && (
            <div className="text-center py-16 text-gray-500">Ready</div>
          )}
        </div>
      </div>
    );
  },
);

AgentCanvas.displayName = "AgentCanvas";
