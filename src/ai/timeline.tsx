/**
 * Chronological event timeline.
 */
import React from 'react';

export interface TimelineEvent {
  date: string;
  title: string;
  description: any;
}

export interface TimelineProps {
  events?: TimelineEvent[];
  className?: string;
}

function TimelineComponent({ events = [], className }: TimelineProps) {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-6 ${className}`}>
      <div className="space-y-6">
        {events.map((event, index) => (
          <div key={index} className="border-l-4 border-blue-500 pl-6 relative">
            <div className="absolute top-0 w-3 h-3 bg-blue-500 rounded-full -ml-8 mt-1"></div>
            <div className="font-semibold text-gray-900 dark:text-gray-100 text-lg">{event.title}</div>
            <div className="text-sm text-blue-600 dark:text-blue-400 font-medium mb-2">{event.date}</div>
            <div className="text-gray-600 dark:text-gray-300">{event.description}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export const Timeline = TimelineComponent;

// AgentInterface Metadata - autodiscovery pattern
export const TimelineMetadata = {
  type: 'timeline',
  description: 'Sequential events display with dates',
  schema: {
    type: 'object',
    properties: {
      events: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            date: { type: 'string' },
            title: { type: 'string' },
            description: { type: 'any' }
          },
          required: ['date', 'title', 'description']
        }
      },
      className: { type: 'string', optional: true }
    },
    required: ['events']
  },
  category: 'data'
};