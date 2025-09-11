import React from 'react';

export interface ImageProps {
  src: string;
  alt: string;
  caption?: string;
  href?: string;
  className?: string;
}

function ImageComponent({ src, alt, caption, href, className }: ImageProps) {
  const image = (
    <img
      src={src}
      alt={alt}
      className="max-w-full h-auto rounded-lg"
      loading="lazy"
    />
  );

  const content = (
    <div className={className}>
      {href ? (
        <a href={href} target="_blank" rel="noopener noreferrer">
          {image}
        </a>
      ) : (
        image
      )}
      {caption && (
        <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">{caption}</div>
      )}
    </div>
  );

  return content;
}

export const Image = ImageComponent;

// AgentInterface Metadata - autodiscovery pattern
export const ImageMetadata = {
  type: 'image',
  description: 'Single image with optional caption and link',
  schema: {
    type: 'object',
    properties: {
      src: { type: 'string' },
      alt: { type: 'string' },
      caption: { type: 'string', optional: true },
      href: { type: 'string', optional: true },
      className: { type: 'string', optional: true }
    },
    required: ['src', 'alt']
  },
  category: 'media'
};