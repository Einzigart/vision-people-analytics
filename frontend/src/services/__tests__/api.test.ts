/**
 * Unit tests for the simplified API service utility functions.
 * Tests utility functions and error handling.
 */

import { describe, it, expect, vi } from 'vitest';
import { apiUtils, handleApiError, AGE_GROUPS, calculateDemographicsTotal, getGenderPercentages } from '../api';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('ApiUtils', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
  });

  it('should check authentication status', () => {
    localStorageMock.getItem.mockReturnValue('token');
    expect(apiUtils.isAuthenticated()).toBe(true);

    localStorageMock.getItem.mockReturnValue(null);
    expect(apiUtils.isAuthenticated()).toBe(false);
  });

  it('should get user data', () => {
    const userData = { id: 1, username: 'test' };
    localStorageMock.getItem.mockReturnValue(JSON.stringify(userData));

    expect(apiUtils.getUserData()).toEqual(userData);
  });

  it('should clear auth data', () => {
    apiUtils.clearAuth();

    expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('user_data');
  });

  it('should format date correctly', () => {
    const date = new Date('2025-01-18');
    expect(apiUtils.formatDate(date)).toBe('2025-01-18');
  });

  it('should get date ranges correctly', () => {
    const mockToday = new Date('2025-01-18');
    vi.spyOn(globalThis, 'Date').mockImplementation(() => mockToday as any);

    const today = apiUtils.getDateRange('today');
    expect(today.startDate.toDateString()).toBe(today.endDate.toDateString());

    const yesterday = apiUtils.getDateRange('yesterday');
    expect(yesterday.startDate.getDate()).toBe(17);

    const last7days = apiUtils.getDateRange('last7days');
    expect(last7days.startDate.getDate()).toBe(11);

    const last30days = apiUtils.getDateRange('last30days');
    expect(last30days.startDate.getDate()).toBe(19); // Previous month

    vi.restoreAllMocks();
  });
});

describe('Demographics Utilities', () => {
  it('should calculate demographics total correctly', () => {
    const demographics = {
      male: { '20-29': 10, '30-39': 5 },
      female: { '20-29': 15, '30-39': 8 }
    };

    const total = calculateDemographicsTotal(demographics);
    expect(total).toBe(38); // 10 + 5 + 15 + 8
  });

  it('should calculate gender percentages correctly', () => {
    const demographics = {
      male: { '20-29': 20 },
      female: { '20-29': 30 }
    };

    const percentages = getGenderPercentages(demographics);
    expect(percentages.male).toBe(40); // 20/50 * 100
    expect(percentages.female).toBe(60); // 30/50 * 100
  });

  it('should handle empty demographics', () => {
    const demographics = {
      male: {},
      female: {}
    };

    const total = calculateDemographicsTotal(demographics);
    expect(total).toBe(0);

    const percentages = getGenderPercentages(demographics);
    expect(percentages.male).toBe(0);
    expect(percentages.female).toBe(0);
  });
});

describe('Constants', () => {
  it('should have correct age groups', () => {
    expect(AGE_GROUPS).toEqual(['0-9', '10-19', '20-29', '30-39', '40-49', '50+']);
  });
});

describe('handleApiError', () => {
  it('should handle response errors correctly', () => {
    const error400 = { response: { status: 400, data: { detail: 'Bad request' } } };
    expect(handleApiError(error400)).toBe('Bad request');

    const error401 = { response: { status: 401, data: {} } };
    expect(handleApiError(error401)).toBe('Invalid username or password');

    const error403 = { response: { status: 403, data: {} } };
    expect(handleApiError(error403)).toBe('Access forbidden');

    const error404 = { response: { status: 404, data: {} } };
    expect(handleApiError(error404)).toBe('Resource not found');

    const error500 = { response: { status: 500, data: {} } };
    expect(handleApiError(error500)).toBe('Internal server error');
  });

  it('should handle network errors', () => {
    const networkError = { request: {} };
    expect(handleApiError(networkError)).toBe('Network error. Please check your connection.');
  });

  it('should handle other errors', () => {
    const otherError = { message: 'Something went wrong' };
    expect(handleApiError(otherError)).toBe('Something went wrong');

    const unknownError = {};
    expect(handleApiError(unknownError)).toBe('An unexpected error occurred');
  });
});
