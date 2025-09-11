/**
 * Generic card layout component.
 */
import React from 'react';
import type { CallbackEvent } from '../types';

export interface CardProps {
  title?: string;
  content?: string;
  actions?: any[];
  className?: string;
  variant?: 'default' | 'outlined' | 'elevated';
  onCallback?: (event: CallbackEvent) => void;
}

function CardComponent({
  title,
  content,
  actions,
  className = '',
  variant = 'default',
  onCallback,
}: CardProps) {
  
  const handleClick = () => {
    onCallback?.({
      type: 'click',
      component: 'card',
      data: { title, content }
    });
  };
  const baseStyles = 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg';
  const variantStyles = {
    default: '',
    outlined: 'border-2',
    elevated: 'shadow-md'
  };

  return (
    <div 
      className={`${baseStyles} ${variantStyles[variant]} ${onCallback ? 'cursor-pointer hover:shadow-sm transition-shadow' : ''} ${className}`}
      onClick={onCallback ? handleClick : undefined}
    >
      {title && (
        <div className="px-4 pt-4 pb-2">
          <h3 className="font-medium text-gray-900 dark:text-gray-100">{title}</h3>
        </div>
      )}
      {content && (
        <div className="px-4 pb-4 text-gray-600 dark:text-gray-400">
          {content}
        </div>
      )}
      {actions && (
        <div className="px-4 pb-4 flex gap-2">
          {actions.map((action, i) => (
            <button 
              key={i}
              className="px-3 py-1.5 text-sm bg-gray-900 hover:bg-gray-800 dark:bg-gray-100 dark:hover:bg-gray-200 text-white dark:text-gray-900 rounded transition-colors"
            >
              {action}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export const Card = CardComponent;

// AgentInterface Metadata - autodiscovery pattern
export const CardMetadata = {
  type: 'card',
  description: 'Generic card with title, content and actions',
  schema: {
    type: 'object',
    properties: {
      title: { type: 'string', optional: true },
      content: { type: 'string', optional: true },
      actions: { type: 'array', items: { type: 'string' }, optional: true },
      variant: { type: 'string', enum: ['default', 'outlined', 'elevated'], optional: true },
      className: { type: 'string', optional: true }
    },
    required: []
  },
  category: 'layout'
};
