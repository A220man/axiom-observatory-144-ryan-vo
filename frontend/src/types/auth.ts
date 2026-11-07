export interface UserInfo {
  sub: string;
  preferred_username?: string;
  email?: string;
  name?: string;
  roles: string[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
  scope?: string;
}

export interface LoginUrlResponse {
  login_url: string;
  state: string;
  code_challenge: string;
  code_challenge_method: string;
}

export interface CallbackRequest {
  code: string;
  state: string;
  code_verifier: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: UserInfo | null;
  accessToken: string | null;
  loading: boolean;
  error: string | null;
}
