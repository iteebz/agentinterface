import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Accordion } from '../../src/ai/accordion';

describe('Accordion', () => {
  it('toggles expanded state and exposes aria attributes', () => {
    render(
      <Accordion
        sections={[
          { title: 'Overview', content: 'Summary content' },
          { title: 'Details', content: 'Deep dive' },
        ]}
      />
    );

    const button = screen.getByRole('button', { name: 'Overview' });
    expect(button).toHaveAttribute('aria-expanded', 'false');

    fireEvent.click(button);
    expect(button).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByRole('region', { name: 'Overview' })).toBeInTheDocument();
  });
});
