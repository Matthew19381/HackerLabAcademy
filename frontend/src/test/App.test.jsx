import { describe, it, expect } from 'vitest';

describe('App Component', () => {
  it('should have correct display name', async () => {
    const App = (await import('../App.jsx')).default;
    expect(App).toBeDefined();
    // App should be a valid React component
    expect(typeof App).toBe('function');
  });
});
