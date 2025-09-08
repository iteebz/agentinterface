/**
 * Human prose and writing content renderer.
 */
export { Prose } from '../prose';

// AIP Metadata - autodiscovery pattern
export const metadata = {
  type: 'prose',
  description: 'Human prose and writing content',
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