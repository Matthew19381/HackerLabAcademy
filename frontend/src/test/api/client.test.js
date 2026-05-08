import { describe, it, expect, beforeEach } from 'vitest';
import { getUserId, setUserId, clearUser } from '../../api/client.js';

describe('API Client - localStorage functions', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should return null when no user_id in localStorage', () => {
    const userId = getUserId();
    expect(userId).toBeNull();
  });

  it('should return user_id when set in localStorage', () => {
    setUserId(123);
    const userId = getUserId();
    expect(userId).toBe(123);
  });

  it('should clear user_id from localStorage', () => {
    setUserId(456);
    clearUser();
    const userId = getUserId();
    expect(userId).toBeNull();
  });
});
