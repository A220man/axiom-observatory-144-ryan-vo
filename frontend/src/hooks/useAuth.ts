import { useState, useCallback, useEffect } from 'react';
import type { AuthState } from '../types/auth';
import { apiClient } from '../api/client';

const STORAGE_KEY = 'axiom_auth';

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    accessToken: null,
    loading: true,
    error: null,
  });

  // Load auth state from sessionStorage on mount
  useEffect(() => {
    const stored = sessionStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setState({
          isAuthenticated: true,
          user: parsed.user,
          accessToken: parsed.accessToken,
          loading: false,
          error: null,
        });
        // Set token in apiClient
        apiClient.setAuthToken(parsed.accessToken);
      } catch {
        sessionStorage.removeItem(STORAGE_KEY);
        setState(prev => ({ ...prev, loading: false }));
      }
    } else {
      setState(prev => ({ ...prev, loading: false }));
    }
  }, []);

  const login = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const loginResponse = await apiClient.authLogin();
      // Store code_verifier and state for callback
      sessionStorage.setItem('axiom_pkce', JSON.stringify({
        code_verifier: loginResponse.code_challenge,
        state: loginResponse.state,
      }));
      // Redirect to Keycloak
      window.location.href = loginResponse.login_url;
    } catch (err) {
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: err instanceof Error ? err.message : 'Login failed' 
      }));
    }
  }, []);

  const handleCallback = useCallback(async (code: string, state: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      // Retrieve PKCE data
      const pkceData = sessionStorage.getItem('axiom_pkce');
      if (!pkceData) {
        throw new Error('Missing PKCE data');
      }
      const { code_verifier, state: storedState } = JSON.parse(pkceData);
      
      if (state !== storedState) {
        throw new Error('Invalid state');
      }

      const tokenResponse = await apiClient.authCallback({ code, state, code_verifier });
      
      // Fetch user info
      const user = await apiClient.authMe();
      
      const authData = {
        user,
        accessToken: tokenResponse.access_token,
      };
      
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(authData));
      sessionStorage.removeItem('axiom_pkce');
      
      apiClient.setAuthToken(tokenResponse.access_token);
      
      setState({
        isAuthenticated: true,
        user,
        accessToken: tokenResponse.access_token,
        loading: false,
        error: null,
      });
    } catch (err) {
      sessionStorage.removeItem('axiom_pkce');
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: err instanceof Error ? err.message : 'Callback failed' 
      }));
    }
  }, []);

  const logout = useCallback(() => {
    sessionStorage.removeItem(STORAGE_KEY);
    sessionStorage.removeItem('axiom_pkce');
    apiClient.setAuthToken(null);
    setState({
      isAuthenticated: false,
      user: null,
      accessToken: null,
      loading: false,
      error: null,
    });
  }, []);

  return {
    ...state,
    login,
    handleCallback,
    logout,
  };
}
