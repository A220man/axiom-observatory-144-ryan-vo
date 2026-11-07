import type { BenchmarkRequest, BenchmarkResponse, HealthResponse } from '../types/api';
import type { TokenResponse, LoginUrlResponse, UserInfo, CallbackRequest } from '../types/auth';

const API_BASE = '/api/v1';

let authToken: string | null = null;

function setAuthToken(token: string | null) {
  authToken = token;
}

function getAuthHeaders(): HeadersInit {
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
  return headers;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export const apiClient = {
  setAuthToken,
  
  async health(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE}/health`);
    return handleResponse<HealthResponse>(response);
  },

  async benchmark(request: BenchmarkRequest): Promise<BenchmarkResponse> {
    const response = await fetch(`${API_BASE}/benchmark`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(request),
    });
    return handleResponse<BenchmarkResponse>(response);
  },

  async authLogin(): Promise<LoginUrlResponse> {
    const response = await fetch(`${API_BASE}/auth/login`);
    return handleResponse<LoginUrlResponse>(response);
  },

  async authCallback(request: CallbackRequest): Promise<TokenResponse> {
    const response = await fetch(`${API_BASE}/auth/callback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    return handleResponse<TokenResponse>(response);
  },

  async authMe(): Promise<UserInfo> {
    const response = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<UserInfo>(response);
  },

  async authLogout(): Promise<void> {
    await fetch(`${API_BASE}/auth/logout`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
  },
};
