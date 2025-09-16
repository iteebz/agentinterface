import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Tabs } from '../../src/ai/tabs';

describe('Tabs', () => {
  it('changes active tab via keyboard input', () => {
    render(
      <Tabs
        items={[
          { id: 'summary', label: 'Summary', content: <div>Summary panel</div> },
          { id: 'details', label: 'Details', content: <div>Detail panel</div> },
        ]}
      />
    );

    const firstTab = screen.getByRole('tab', { name: 'Summary' });
    const secondTab = screen.getByRole('tab', { name: 'Details' });

    expect(firstTab).toHaveAttribute('aria-selected', 'true');
    expect(secondTab).toHaveAttribute('aria-selected', 'false');
    expect(screen.getByText('Summary panel')).toBeInTheDocument();

    fireEvent.keyDown(firstTab, { key: 'ArrowRight' });

    expect(secondTab).toHaveAttribute('aria-selected', 'true');
    expect(document.activeElement).toBe(secondTab);
    expect(screen.getByText('Detail panel')).toBeInTheDocument();
  });
});
