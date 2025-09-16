import React, { useId, useState } from 'react';
import type { CallbackEvent } from '../types';

export interface AccordionSection {
  title: string;
  content: any;
  defaultExpanded?: boolean;
}

export interface AccordionProps {
  sections?: AccordionSection[];
  className?: string;
  onCallback?: (event: CallbackEvent) => void;
}

function AccordionComponent({ sections = [], className, onCallback }: AccordionProps) {
  const instanceId = useId();
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
      {sections.map((section, index) => {
        const triggerId = `${instanceId}-accordion-trigger-${index}`;
        const panelId = `${instanceId}-accordion-panel-${index}`;

        return (
          <div
            key={index}
            className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-all duration-200 mb-4"
          >
            <button
              type="button"
              className="w-full p-6 text-left font-semibold text-gray-900 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors rounded-xl"
              onClick={() => toggle(index)}
              id={triggerId}
              aria-expanded={openSections.has(index)}
              aria-controls={panelId}
            >
              {section.title}
            </button>
            {openSections.has(index) && (
              <div
                id={panelId}
                role="region"
                aria-labelledby={triggerId}
                className="px-4 pb-4 border-t border-gray-200 dark:border-gray-700 pt-4"
              >
                {section.content}
              </div>
            )}
          </div>
        );
      })}
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
            content: { type: 'any' },
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
