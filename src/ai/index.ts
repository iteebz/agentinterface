/**
 * AIP Components Index
 *
 * This directory contains AgentInterface Protocol (AIP) components that follow
 * the standardized metadata pattern for build-time discovery and registry generation.
 *
 * Each component in this directory should:
 * 1. Export a metadata object with type, description, schema, and category
 * 2. Follow the standardized naming convention
 * 3. Include proper JSON Schema for validation
 *
 * Components are automatically discovered during build time and included
 * in the generated registry for Python consumption.
 */

// Core AIP Components - All with metadata exports
export { Timeline, metadata as TimelineMetadata } from './timeline';
export { Prose, metadata as ProseMetadata } from './prose';
export { Table, metadata as TableMetadata } from './table';
export { Reference, metadata as ReferenceMetadata } from './reference';
export { Gallery, metadata as GalleryMetadata } from './gallery';
export { Accordion, metadata as AccordionMetadata } from './accordion';
export { Tree, metadata as TreeMetadata } from './tree';
export { Suggestions, metadata as SuggestionsMetadata } from './suggestions';
export { Code, metadata as CodeMetadata } from './code';
export { Card, metadata as CardMetadata } from './card';
export { Tabs, metadata as TabsMetadata } from './tabs';
