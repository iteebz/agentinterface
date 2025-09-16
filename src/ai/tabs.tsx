import React, { useState } from 'react';
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
  const [activeTab, setActiveTab] = useState(defaultTab || items[0]?.id || '');
  
  const handleTabChange = (tabId: string, label: string) => {
    setActiveTab(tabId);
    onCallback?.({
      type: 'change',
      component: 'tabs',
      data: { id: tabId, label }
    });
  };

  const activeContent =
    items.find((item) => item.id === activeTab)?.content || '';

  if (items.length === 0) return null;

  return (
    <div className={className}>
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          {items.map((item) => (
            <button
              key={item.id}
              className={`px-6 py-3 text-sm font-medium transition-colors rounded-t-xl ${
                activeTab === item.id
                  ? 'text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 border-b-2 border-blue-500'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
              onClick={() => handleTabChange(item.id, item.label)}
            >
              {item.label}
            </button>
          ))}
        </div>
        <div className="p-6">
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
