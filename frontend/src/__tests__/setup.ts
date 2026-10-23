import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';

// Import jest-dom matchers
import '@testing-library/jest-dom';

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});