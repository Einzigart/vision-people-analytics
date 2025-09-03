/** API client for consolidated backend endpoints. */

import axios from 'axios';

// Retry wrapper with backoff for transient errors
const retryApiCall = async <T>(
  apiCall: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  let lastError: any;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await apiCall();
    } catch (error: any) {
      lastError = error;

      // Don't retry on authentication errors or client errors (4xx)
      if (error.response?.status >= 400 && error.response?.status < 500) {
        throw error;
      }

      // Don't retry on the last attempt
      if (attempt === maxRetries) {
        break;
      }

      console.warn(`API call failed (attempt ${attempt}/${maxRetries}):`, error.message);

      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay * attempt));
    }
  }

  throw lastError;
};

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle authentication errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Types
export interface AuthResponse {
  token: string;
  user_id: number;
  username: string;
}

export interface User {
  id: number;
  username: string;
}

export interface BasicTotals {
  male: number;
  female: number;
  total: number;
}

export interface Demographics {
  male: Record<string, number>;
  female: Record<string, number>;
}

export interface ModelSettings {
  id: number;
  confidence_threshold_person: number;
  confidence_threshold_face: number;
  log_interval_seconds: number;
  last_updated: string;
  updated_by: User | null;
}

// Legacy interfaces for backward compatibility
export interface TodayStats {
  date: string;
  totals: BasicTotals;
  percentages: { male: number; female: number };
  hourly_breakdown: Record<string, BasicTotals>;
  hourly_data?: Record<string, BasicTotals>;
  last_detection?: string;
}

export interface TodayAgeGenderStats {
  date: string;
  demographics: Demographics;
  totals: BasicTotals;
  percentages: { male: number; female: number };
  hourly_breakdown: Record<string, { demographics: Demographics; totals: BasicTotals }>;
}

// Age group constants and types
export const AGE_GROUPS = ['0-9', '10-19', '20-29', '30-39', '40-49', '50+'] as const;
export const GENDERS = ['male', 'female'] as const;

export type AgeGroup = typeof AGE_GROUPS[number];
export type Gender = typeof GENDERS[number];

// API Service Class
class ApiService {
  // Authentication
  async login(username: string, password: string): Promise<AuthResponse> {
    const response = await retryApiCall(() =>
      api.post('/auth/login/', { username, password })
    );
    localStorage.setItem('auth_token', response.data.token);
    localStorage.setItem('user_data', JSON.stringify({
      id: response.data.user_id,
      username: response.data.username,
    }));
    return response.data;
  }

  logout(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  }

  getUserData(): User | null {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  }

  getCurrentUser(): User | null {
    return this.getUserData();
  }

  // NEW CONSOLIDATED ENDPOINTS (Phase 2)
  async getTodayStats(includeDemographics: boolean = false): Promise<any> {
    const params = includeDemographics ? { include_demographics: 'true' } : {};
    const response = await retryApiCall(() =>
      api.get('/stats/today/', { params })
    );
    return response.data;
  }

  async getRangeStats(startDate: string, endDate: string, includeDemographics: boolean = false): Promise<any> {
    const params = includeDemographics ? { include_demographics: 'true' } : {};
    const response = await retryApiCall(() =>
      api.get(`/stats/range/${startDate}/${endDate}/`, { params })
    );
    return response.data;
  }

  // Detection data
  async submitDetectionData(data: any): Promise<any> {
    const response = await retryApiCall(() =>
      api.post('/detections/', data)
    );
    return response.data;
  }

  async getDetectionLogs(): Promise<any> {
    const response = await retryApiCall(() =>
      api.get('/detections/')
    );
    return response.data;
  }

  // Aggregation data
  async getDailyAggregation(params?: any): Promise<any> {
    const response = await api.get('/daily/', { params });
    return response.data;
  }

  async getMonthlyAggregation(params?: any): Promise<any> {
    const response = await api.get('/monthly/', { params });
    return response.data;
  }

  // Settings
  async getModelSettings(): Promise<ModelSettings> {
    const response = await api.get('/settings/');
    return response.data;
  }

  async updateModelSettings(settings: Partial<ModelSettings>): Promise<ModelSettings> {
    const response = await api.put('/settings/', settings);
    return response.data;
  }

  async getPublicModelSettings(): Promise<any> {
    const response = await api.get('/public-settings/');
    return response.data;
  }

  // Export
  async exportData(format: 'csv' | 'pdf', startDate: string, endDate: string): Promise<Blob> {
    const response = await api.get('/export/', {
      params: { format, start_date: startDate, end_date: endDate },
      responseType: 'blob',
    });
    return response.data;
  }

  // LEGACY ENDPOINTS (for backward compatibility)
  async getTodayStatsLegacy(): Promise<any> {
    const response = await api.get('/today/');
    return response.data;
  }

  async getTodayAgeGenderStats(): Promise<any> {
    // Use consolidated endpoint with demographics
    return this.getTodayStats(true);
  }

  async getAnalyticsData(startDate: Date, endDate: Date): Promise<any> {
    const start = startDate.toLocaleDateString('en-CA');
    const end = endDate.toLocaleDateString('en-CA');
    // Use the optimized consolidated endpoint with retry logic
    const response = await retryApiCall(() =>
      api.get(`/stats/range/${start}/${end}/`)
    );
    return response.data;
  }

  async getAgeGenderDateRangeStats(startDate: Date, endDate: Date): Promise<any> {
    const start = startDate.toLocaleDateString('en-CA');
    const end = endDate.toLocaleDateString('en-CA');
    // Use the optimized consolidated endpoint with demographics
    const response = await retryApiCall(() =>
      api.get(`/stats/range/${start}/${end}/`, { params: { include_demographics: 'true' } })
    );
    return response.data;
  }

  async getAgeGenderAnalyticsData(startDate: string, endDate: string, opts?: { noCache?: boolean }): Promise<any> {
    // Ensure dates are in the correct format (YYYY-MM-DD) without timezone conversion
    const formatForApi = (dateStr: string): string => {
      const date = new Date(dateStr);
      // Format as YYYY-MM-DD without timezone conversion
      return date.getFullYear() + '-' + 
             String(date.getMonth() + 1).padStart(2, '0') + '-' + 
             String(date.getDate()).padStart(2, '0');
    };
    
    const formattedStartDate = formatForApi(startDate);
    const formattedEndDate = formatForApi(endDate);
    
    // Use the optimized consolidated endpoint with demographics
    const params: Record<string, string> = { include_demographics: 'true' };
    if (opts?.noCache) params['no_cache'] = 'true';
    const response = await retryApiCall(() =>
      api.get(`/stats/range/${formattedStartDate}/${formattedEndDate}/`, { params })
    );

    // Defensive normalization for hourly payloads to ensure consistent shape:
    // - Ensure hourly `data` object contains keys "0".."23"
    // - Ensure male/female/total are numbers (fallback to 0)
    // This prevents Recharts from encountering undefined domains when switching granularities.
    const payload = response.data || {};

    try {
      if (payload.type === 'hourly') {
        const src = payload.data || payload.hourly_data || {};
        const normalized: Record<string, { male: number; female: number; total: number }> = {};
        for (let h = 0; h < 24; h++) {
          const key = String(h);
          const entry = src[key] || src[key.padStart(2, '0')] || {};
          const male = Number(entry?.male ?? entry?.m ?? 0);
          const female = Number(entry?.female ?? entry?.f ?? 0);
          const totalRaw = entry?.total ?? (male + female);
          const total = Number(totalRaw);
          normalized[key] = {
            male: Number.isFinite(male) ? male : 0,
            female: Number.isFinite(female) ? female : 0,
            total: Number.isFinite(total) ? total : (Number.isFinite(male + female) ? male + female : 0),
          };
        }
        // Replace payload.data with normalized hourly data so consumers always receive expected shape
        payload.data = normalized;
      }

      // When the API returns an unexpected shape but the caller requested a single-day range,
      // we still return the payload but leave UI to decide whether to render or show loading.
      return payload;
    } catch (err) {
      // If normalization fails for any reason, return original response to avoid hiding errors.
      console.error('Error normalizing analytics payload:', err);
      return response.data;
    }
  }

  async triggerDataAggregation(): Promise<{ status: string; message: string; success: boolean; stats?: any }> {
    try {
      // Use a longer timeout for aggregation (2 minutes)
      const response = await api.post('/trigger-aggregation/', {}, {
        timeout: 120000 // 2 minutes timeout
      });

      // Transform backend response to match frontend expectations
      return {
        status: response.data.success ? 'success' : 'error',
        message: response.data.message,
        success: response.data.success,
        stats: response.data.stats
      };
    } catch (error: any) {
      console.error('Error triggering aggregation:', error);

      // Check if it's a timeout error
      if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
        return {
          status: 'warning',
          message: 'Aggregation is taking longer than expected but may still be running. Please check the results in a few minutes.',
          success: true // Consider it successful since it's likely still processing
        };
      }

      return {
        status: 'error',
        message: error.response?.data?.message || 'Failed to trigger data aggregation',
        success: false
      };
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;

// Utility functions
export const apiUtils = {
  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  },

  getUserData(): any {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  },

  clearAuth(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
  },

  formatDate(date: Date): string {
    return date.toLocaleDateString('en-CA'); // YYYY-MM-DD format
  },

  getDateRange(period: 'today' | 'yesterday' | 'last7days' | 'last30days'): { startDate: Date; endDate: Date } {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    switch (period) {
      case 'today':
        return { startDate: today, endDate: today };
      case 'yesterday': {
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        return { startDate: yesterday, endDate: yesterday };
      }
      case 'last7days': {
        const week = new Date(today);
        week.setDate(week.getDate() - 7);
        return { startDate: week, endDate: today };
      }
      case 'last30days': {
        const month = new Date(today);
        month.setDate(month.getDate() - 30);
        return { startDate: month, endDate: today };
      }
      default:
        return { startDate: today, endDate: today };
    }
  },
};

// Date utility functions
export const formatDateForApi = (date: Date): string => {
  // Format as YYYY-MM-DD without timezone conversion
  return date.getFullYear() + '-' + 
         String(date.getMonth() + 1).padStart(2, '0') + '-' + 
         String(date.getDate()).padStart(2, '0');
};

export const parseApiDate = (dateString: string): Date => {
  return new Date(dateString);
};

// Demographics utility functions
export const calculateDemographicsTotal = (demographics: Demographics): number => {
  const maleTotal = Object.values(demographics.male).reduce((sum, count) => sum + count, 0);
  const femaleTotal = Object.values(demographics.female).reduce((sum, count) => sum + count, 0);
  return maleTotal + femaleTotal;
};

export const getAgeGroupPercentages = (demographics: Demographics): Record<AgeGroup, number> => {
  const total = calculateDemographicsTotal(demographics);
  const percentages: Record<string, number> = {};

  AGE_GROUPS.forEach(ageGroup => {
    const maleCount = demographics.male[ageGroup] || 0;
    const femaleCount = demographics.female[ageGroup] || 0;
    const ageGroupTotal = maleCount + femaleCount;
    percentages[ageGroup] = total > 0 ? (ageGroupTotal / total) * 100 : 0;
  });

  return percentages as Record<AgeGroup, number>;
};

export const getGenderPercentages = (demographics: Demographics): Record<Gender, number> => {
  const total = calculateDemographicsTotal(demographics);
  const maleTotal = Object.values(demographics.male).reduce((sum, count) => sum + count, 0);
  const femaleTotal = Object.values(demographics.female).reduce((sum, count) => sum + count, 0);

  return {
    male: total > 0 ? (maleTotal / total) * 100 : 0,
    female: total > 0 ? (femaleTotal / total) * 100 : 0,
  };
};

// Error handling utility
export const handleApiError = (error: any): string => {
  if (error.response) {
    const { status, data } = error.response;
    const payloadMsg = data?.detail || data?.message || data?.error;
    if (status === 400) return payloadMsg || 'Invalid request';
    if (status === 401) return payloadMsg || 'Invalid username or password';
    if (status === 403) return payloadMsg || 'Access forbidden';
    if (status === 404) return payloadMsg || 'Resource not found';
    if (status === 500) return payloadMsg || 'Internal server error. Please try again.';
    if (status === 502) return payloadMsg || 'Bad gateway. Server may be temporarily unavailable.';
    if (status === 503) return payloadMsg || 'Service unavailable. Please try again later.';
    if (status === 504) return payloadMsg || 'Gateway timeout. Please try again.';
    return payloadMsg || 'An error occurred';
  } else if (error.request) {
    // Network error - could be connection issues with Supabase
    if (error.code === 'ECONNABORTED') {
      return 'Request timeout. Please check your connection and try again.';
    }
    return 'Network error. Please check your connection.';
  } else {
    return error.message || 'An unexpected error occurred';
  }
};
