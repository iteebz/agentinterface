/**
 * Markdown content renderer with sanitization.
 */
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export interface ProseProps {
  content: string;
  className?: string;
  options?: any;
  onSendMessage?: (message: string) => void;
}

export function Prose({ content, className = '' }: ProseProps) {
  return (
    <div className={`aip-markdown ${className}`}>
      <ReactMarkdown 
        remarkPlugins={[remarkGfm]}
        components={{
          // Sanitize links
          a: ({ href, children }) => (
            <a 
              href={href?.startsWith('javascript:') ? '#' : href}
              target={href?.startsWith('http') ? '_blank' : undefined}
              rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
            >
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
