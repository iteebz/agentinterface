import React, { useState } from 'react';
import type { CallbackEvent } from '../types';

export interface AccordionSection {
  title: string;
  content: string;
  defaultExpanded?: boolean;
}

export interface AccordionProps {
  sections?: AccordionSection[];
  className?: string;
  onCallback?: (event: CallbackEvent) => void;
}

function AccordionComponent({ sections = [], className, onCallback }: AccordionProps) {
  const [openSections, setOpenSections] = useState<Set<number>>(
    new Set(sections.map((section, index) => section.defaultExpanded ? index : -1).filter(i => i >= 0))
  );

  const toggle = (index: number) => {
    const section = sections[index];
    const newOpen = new Set(openSections);
    const isOpening = !newOpen.has(index);
    
    if (newOpen.has(index)) {
      newOpen.delete(index);
    } else {
      newOpen.add(index);
    }
    setOpenSections(newOpen);
    
    onCallback?.({
      type: 'toggle',
      component: 'accordion',
      data: { title: section?.title, expanded: isOpening }
    });
  };

  return (
    <div className={className}>
      {sections.map((section, index) => (
        <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg mb-2 bg-white dark:bg-gray-800">
          <button 
            className="w-full p-4 text-left font-medium text-gray-900 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors rounded-lg"
            onClick={() => toggle(index)}
          >
            {section.title}
          </button>
          {openSections.has(index) && (
            <div className="px-4 pb-4 text-gray-600 dark:text-gray-300 border-t border-gray-200 dark:border-gray-700 pt-4">{section.content}</div>
          )}
        </div>
      ))}
    </div>
  );
}

export const Accordion = AccordionComponent;

// AgentInterface Metadata - autodiscovery pattern
export const AccordionMetadata = {
  type: 'accordion',
  description: 'Collapsible sections with expandable content',
  schema: {
    type: 'object',
    properties: {
      sections: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            title: { type: 'string' },
            content: { type: 'string' },
            defaultExpanded: { type: 'boolean', optional: true }
          },
          required: ['title', 'content']
        }
      },
      className: { type: 'string', optional: true }
    },
    required: ['sections']
  },
  category: 'layout'
};