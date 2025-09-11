import React from 'react';

export interface TableItem {
  id: string;
  name: string;
  attributes: Record<string, any>;
}

export interface TableAttribute {
  key: string;
  label: string;
}

export interface TableProps {
  items: TableItem[];
  attributes: TableAttribute[];
  title?: string;
  className?: string;
}

function TableComponent({ items, attributes, title, className }: TableProps) {
  return (
    <div className={className}>
      {title && <h2 className="mb-4 text-xl font-bold">{title}</h2>}
      <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
        <table className="w-full bg-white dark:bg-gray-800">
          <thead>
            <tr className="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
              <th className="px-4 py-3 text-left font-medium text-gray-900 dark:text-gray-100">Name</th>
              {attributes.map((attr) => (
                <th key={attr.key} className="px-4 py-3 text-left font-medium text-gray-900 dark:text-gray-100">
                  {attr.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-200 dark:border-gray-600 transition-colors">
                <td className="px-4 py-3 font-medium text-gray-900 dark:text-gray-100">{item.name}</td>
                {attributes.map((attr) => (
                  <td key={attr.key} className="px-4 py-3 text-gray-600 dark:text-gray-300">
                    {String(item.attributes[attr.key] || '—')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export const Table = TableComponent;

// AgentInterface Metadata - autodiscovery pattern
export const TableMetadata = {
  type: 'table',
  description: 'Structured data display with rows and columns',
  schema: {
    type: 'object',
    properties: {
      items: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            name: { type: 'string' },
            attributes: { type: 'object' }
          },
          required: ['id', 'name', 'attributes']
        }
      },
      attributes: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            key: { type: 'string' },
            label: { type: 'string' }
          },
          required: ['key', 'label']
        }
      },
      title: { type: 'string', optional: true },
      className: { type: 'string', optional: true }
    },
    required: ['items', 'attributes']
  },
  category: 'data'
};