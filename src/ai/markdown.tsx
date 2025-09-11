import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

export interface MarkdownProps {
  content: string;
  className?: string;
}

function MarkdownComponent({ content, className = '' }: MarkdownProps) {
  return (
    <div className={`markdown ${className}`}>
      <ReactMarkdown 
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ href, children }) => (
            <a 
              href={href?.startsWith('javascript:') ? '#' : href}
              target={href?.startsWith('http') ? '_blank' : undefined}
              rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
            >
              {children}
            </a>
          ),
          code: ({ node, inline, className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <SyntaxHighlighter
                style={oneDark}
                language={match[1]}
                PreTag="div"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

export const Markdown = MarkdownComponent;

// AgentInterface Metadata - autodiscovery pattern
export const MarkdownMetadata = {
  type: 'markdown',
  description: 'Markdown content with syntax highlighting',
  schema: {
    type: 'object',
    properties: {
      content: { type: 'string' },
      className: { type: 'string', optional: true }
    },
    required: ['content']
  },
  category: 'content'
};