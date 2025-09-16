import { describe, it, expect } from 'vitest';
import { formatLLM, type CallbackEvent } from '../src/types';

describe('formatLLM', () => {
  const baseEvent: CallbackEvent = {
    type: 'click',
    component: 'card',
    data: {},
  };

  it('maps known actions to readable phrases', () => {
    expect(formatLLM(baseEvent)).toBe('User clicked card');
    expect(
      formatLLM({ ...baseEvent, type: 'change', data: { label: 'Revenue' } })
    ).toBe('User changed card: Revenue');
  });

  it('falls back gracefully when no detail present', () => {
    const result = formatLLM({ ...baseEvent, type: 'toggle', component: 'accordion' });
    expect(result).toBe('User toggled accordion');
  });
});
