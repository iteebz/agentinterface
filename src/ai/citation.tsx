import React, { useState } from 'react';
import type { CallbackEvent } from '../types';

interface CitationItem {
  id: string;
  title: string;
  type: string;
  excerpt: string;
  content: string;
  url?: string;
}

interface CitationProps {
  citations: CitationItem[];
  className?: string;
  onCallback?: (event: CallbackEvent) => void;
}

function CitationComponent(props: CitationProps) {
  const { citations, className, onCallback } = props;
  const [expandedRefs, setExpandedRefs] = useState<Set<string>>(new Set());

  const toggleExpanded = (refId: string) => {
    const citation = citations.find(c => c.id === refId);
    setExpandedRefs((prev) => {
      const newSet = new Set(prev);
      const isOpening = !newSet.has(refId);
      
      if (newSet.has(refId)) {
        newSet.delete(refId);
      } else {
        newSet.add(refId);
      }
      
      onCallback?.({
        type: 'toggle',
        component: 'citation',
        data: { title: citation?.title, expanded: isOpening }
      });
      
      return newSet;
    });
  };

  return (
    <div className={className}>
      <div className="space-y-2">
        <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Sources:</div>
        {citations.map((citation) => (
          <div key={citation.id}>
            <button
              onClick={() => toggleExpanded(citation.id)}
              className="text-gray-900 dark:text-gray-100 hover:text-gray-600 dark:hover:text-gray-400 text-sm hover:underline font-medium transition-colors"
            >
              {citation.title}
            </button>
            {expandedRefs.has(citation.id) && (
              <div className="ml-4 mt-2 border-l-2 border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 p-3 rounded-r-lg">
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-1 uppercase">{citation.type}</div>
                <div className="text-sm text-gray-700 dark:text-gray-300 mb-2">{citation.excerpt}</div>
                <div className="text-sm text-gray-900 dark:text-gray-100">{citation.content}</div>
                {citation.url && (
                  <a
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-900 dark:text-gray-100 hover:text-gray-600 dark:hover:text-gray-400 mt-2 block text-xs hover:underline transition-colors"
                  >
                    View source →
                  </a>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export const Citation = CitationComponent;

// AgentInterface Metadata - autodiscovery pattern
export const CitationMetadata = {
  type: 'citation',
  description: 'Source citations with expandable content',
  schema: {
    type: 'object',
    properties: {
      citations: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            title: { type: 'string' },
            type: { type: 'string' },
            excerpt: { type: 'string' },
            content: { type: 'string' },
            url: { type: 'string', optional: true }
          },
          required: ['id', 'title', 'type', 'excerpt', 'content']
        }
      },
      className: { type: 'string', optional: true }
    },
    required: ['citations']
  },
  category: 'content'
};