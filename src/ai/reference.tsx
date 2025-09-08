/**
 * Citations and expandable references.
 */
import React, { useState } from 'react';

interface ReferenceItem {
  id: string;
  title: string;
  type: string;
  excerpt: string;
  content: string;
  url?: string;
}

interface ReferenceProps {
  references: ReferenceItem[];
  className?: string;
}

function ReferenceComponent(props: ReferenceProps) {
  const { references, className } = props;
  const [expandedRefs, setExpandedRefs] = useState<Set<string>>(new Set());

  const toggleExpanded = (refId: string) => {
    setExpandedRefs((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(refId)) {
        newSet.delete(refId);
      } else {
        newSet.add(refId);
      }
      return newSet;
    });
  };

  return (
    <div className={className}>
      <div className="space-y-2">
        <div className="text-sm font-medium">References:</div>
        {references.map((reference) => (
          <div key={reference.id}>
            <button
              onClick={() => toggleExpanded(reference.id)}
              className="text-blue-600 hover:text-blue-800 text-sm hover:underline"
            >
              {reference.title}
            </button>
            {expandedRefs.has(reference.id) && (
              <div className="ml-4 mt-2 border-l-2 border-blue-300 bg-blue-50 p-3 rounded-r">
                <div className="text-xs text-gray-600 mb-1 uppercase">{reference.type}</div>
                <div className="text-sm text-gray-700 mb-2">{reference.excerpt}</div>
                <div className="text-sm">{reference.content}</div>
                {reference.url && (
                  <a
                    href={reference.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 mt-2 block text-xs hover:underline"
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

export const Reference = ReferenceComponent;

// AIP Metadata - autodiscovery pattern
export const metadata = {
  type: 'reference',
  description: 'Citations and references with expandable content',
  schema: {
    type: 'object',
    properties: {
      references: {
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
    required: ['references']
  },
  category: 'content'
};