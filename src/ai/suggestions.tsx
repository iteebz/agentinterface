/**
 * Interactive suggestion buttons.
 */
import React from 'react';
import type { CallbackEvent } from '../types';

export interface Suggestion {
  text: string;
  id?: string;
  context?: string;
  priority?: 'high' | 'medium' | 'low';
}

export interface SuggestionsProps {
  suggestions: Suggestion[];
  title?: string;
  className?: string;
  onCallback?: (event: CallbackEvent) => void;
}

function SuggestionsComponent({
  suggestions,
  title = 'Continue the conversation',
  className,
  onCallback,
}: SuggestionsProps) {
  const handleSuggestionClick = (suggestion: Suggestion) => {
    onCallback?.({
      type: 'select',
      component: 'suggestions',
      data: { text: suggestion.text, id: suggestion.id, priority: suggestion.priority }
    });
  };

  return (
    <div className={className}>
      {title && (
        <h4 className="text-sm font-medium text-gray-600 mb-3">{title}</h4>
      )}
      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion, i) => (
          <button
            key={suggestion.id || i}
            onClick={() => handleSuggestionClick(suggestion)}
            className="bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 border border-gray-200 dark:border-gray-600 rounded-full px-3 py-1.5 text-sm text-gray-700 dark:text-gray-300 transition-colors"
          >
            {suggestion.text}
            {suggestion.priority === 'high' && (
              <span className="bg-gray-900 dark:bg-gray-100 ml-1.5 w-1.5 h-1.5 rounded-full inline-block" />
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

export const Suggestions = SuggestionsComponent;

// AgentInterface Metadata - autodiscovery pattern
export const SuggestionsMetadata = {
  type: 'suggestions',
  description: 'Interactive follow-up prompts for conversation',
  schema: {
    type: 'object',
    properties: {
      suggestions: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            text: { type: 'string' },
            id: { type: 'string', optional: true },
            context: { type: 'string', optional: true },
            priority: { type: 'string', enum: ['high', 'medium', 'low'], optional: true }
          },
          required: ['text']
        }
      },
      title: { type: 'string', optional: true },
      className: { type: 'string', optional: true }
    },
    required: ['suggestions']
  },
  category: 'interactive'
};