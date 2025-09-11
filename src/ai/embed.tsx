import React from 'react';

export interface EmbedProps {
  src: string;
  title?: string;
  width?: string;
  height?: string;
  allow?: string;
  className?: string;
}

function EmbedComponent({ 
  src, 
  title, 
  width = "100%", 
  height = "400px", 
  allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture",
  className 
}: EmbedProps) {
  return (
    <div className={className}>
      {title && <div className="text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">{title}</div>}
      <iframe
        src={src}
        title={title || "Embedded content"}
        width={width}
        height={height}
        allow={allow}
        className="border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
        loading="lazy"
      />
    </div>
  );
}

export const Embed = EmbedComponent;

// AgentInterface Metadata - autodiscovery pattern
export const EmbedMetadata = {
  type: 'embed',
  description: 'Embedded iframe content for videos and interactive demos',
  schema: {
    type: 'object',
    properties: {
      src: { type: 'string' },
      title: { type: 'string', optional: true },
      width: { type: 'string', optional: true },
      height: { type: 'string', optional: true },
      allow: { type: 'string', optional: true },
      className: { type: 'string', optional: true }
    },
    required: ['src']
  },
  category: 'media'
};