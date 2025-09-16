import React, { useId, useRef, useState } from 'react';
import type { CallbackEvent } from '../types';

export interface TabItem {
  id: string;
  label: string;
  content: any;
}

export interface TabsProps {
  items?: TabItem[];
  defaultTab?: string;
  className?: string;
  onCallback?: (event: CallbackEvent) => void;
}

function TabsComponent({ items = [], defaultTab, className = '', onCallback }: TabsProps) {
  const instanceId = useId();
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const [activeTab, setActiveTab] = useState(defaultTab || items[0]?.id || '');

  const handleTabChange = (tabId: string, label: string) => {
    setActiveTab(tabId);
    onCallback?.({
      type: 'change',
      component: 'tabs',
      data: { id: tabId, label }
    });
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>, currentIndex: number) => {
    const keys = ['ArrowRight', 'ArrowLeft', 'Home', 'End'];
    if (!keys.includes(event.key)) return;

    event.preventDefault();
    const total = items.length;
    if (!total) return;

    let nextIndex = currentIndex;
    if (event.key === 'ArrowRight') {
      nextIndex = (currentIndex + 1) % total;
    } else if (event.key === 'ArrowLeft') {
      nextIndex = (currentIndex - 1 + total) % total;
    } else if (event.key === 'Home') {
      nextIndex = 0;
    } else if (event.key === 'End') {
      nextIndex = total - 1;
    }

    const nextItem = items[nextIndex];
    if (!nextItem) {
      return;
    }

    handleTabChange(nextItem.id, nextItem.label);
    tabRefs.current[nextIndex]?.focus();
  };

  const activeItem = items.find((item) => item.id === activeTab);
  const activeContent = activeItem?.content || '';

  if (items.length === 0) return null;

  return (
    <div className={className}>
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="flex border-b border-gray-200 dark:border-gray-700" role="tablist" aria-label="Tabbed content">
          {items.map((item, index) => {
            const tabId = `${instanceId}-tab-${item.id}`;
            const panelId = `${instanceId}-panel-${item.id}`;

            return (
              <button
                key={item.id}
                id={tabId}
                type="button"
                role="tab"
                aria-selected={activeTab === item.id}
                aria-controls={panelId}
                tabIndex={activeTab === item.id ? 0 : -1}
                className={`px-6 py-3 text-sm font-medium transition-colors rounded-t-xl ${
                  activeTab === item.id
                    ? 'text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 border-b-2 border-blue-500'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
                ref={(el) => {
                  tabRefs.current[index] = el;
                }}
                onClick={() => handleTabChange(item.id, item.label)}
                onKeyDown={(event) => handleKeyDown(event, index)}
              >
                {item.label}
              </button>
            );
          })}
        </div>
        <div
          id={activeItem ? `${instanceId}-panel-${activeItem.id}` : undefined}
          role="tabpanel"
          aria-labelledby={activeItem ? `${instanceId}-tab-${activeItem.id}` : undefined}
          className="p-6"
        >
          {activeContent}
        </div>
      </div>
    </div>
  );
}

export const Tabs = TabsComponent;

// AgentInterface Metadata - autodiscovery pattern
export const TabsMetadata = {
  type: 'tabs',
  description: 'Tabbed content organization',
  schema: {
    type: 'object',
    properties: {
      items: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            label: { type: 'string' },
            content: { type: 'any' }
          },
          required: ['id', 'label', 'content']
        }
      },
      defaultTab: { type: 'string', optional: true },
      className: { type: 'string', optional: true }
    },
    required: ['items']
  },
  category: 'layout'
};
