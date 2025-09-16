/**
 * Generic card layout component.
 */
import React from 'react';
import type { CallbackEvent } from '../types';

export interface CardProps {
  title?: string;
  content?: any;
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

  const baseStyles = 'bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm hover:shadow-md transition-all duration-200 flex-1';
  const variantStyles = {
    default: '',
    outlined: 'border-2',
    elevated: 'shadow-lg'
  };

  return (
    <div 
      className={`${baseStyles} ${variantStyles[variant]} ${onCallback ? 'cursor-pointer hover:scale-[1.02]' : ''} ${className}`}
      onClick={onCallback ? handleClick : undefined}
    >
      {title && (
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-lg mb-4">
          {title}
        </h3>
      )}
      
      {content && (
        <div className="text-gray-600 dark:text-gray-400">
          {content}
        </div>
      )}
      
      {actions && (
        <div className="mt-4 flex gap-2">
          {actions.map((action, i) => (
            <button 
              key={i}
              type="button"
              className="px-3 py-1.5 text-sm bg-gray-900 hover:bg-gray-800 dark:bg-gray-100 dark:hover:bg-gray-200 text-white dark:text-gray-900 rounded-lg transition-colors"
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

export const CardMetadata = {
  type: 'card',
  description: 'Generic card with title, content and actions',
  schema: {
    type: 'object',
    properties: {
      title: { type: 'string', optional: true },
      content: { type: 'any', optional: true },
      actions: { type: 'array', items: { type: 'string' }, optional: true },
      variant: { type: 'string', enum: ['default', 'outlined', 'elevated'], optional: true },
      className: { type: 'string', optional: true }
    },
    required: []
  },
  category: 'layout'
};
