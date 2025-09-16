import React from 'react';

const SAFE_PROTOCOLS = new Set(['http:', 'https:']);

function sanitizeEmbedSrc(candidate: string): string | null {
  if (!candidate) return null;

  const trimmed = candidate.trim();
  if (!trimmed) return null;

  try {
    const url = new URL(trimmed, 'https://placeholder.local');
    return SAFE_PROTOCOLS.has(url.protocol) ? trimmed : null;
  } catch {
    return null;
  }
}

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
  const sanitizedSrc = sanitizeEmbedSrc(src);

  if (!sanitizedSrc) {
    console.warn('Embed blocked unsafe src value', src);
  }

  return (
    <div className={className}>
      {title && <div className="text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">{title}</div>}
      {sanitizedSrc ? (
        <iframe
          src={sanitizedSrc}
          title={title || "Embedded content"}
          width={width}
          height={height}
          allow={allow}
          className="border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
          loading="lazy"
        />
      ) : (
        <div
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-200"
        >
          Unable to display embed: blocked unsafe source.
        </div>
      )}
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
