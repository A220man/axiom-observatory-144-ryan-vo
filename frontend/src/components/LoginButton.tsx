import { useAuth } from '../hooks/useAuth';

export function LoginButton() {
  const { isAuthenticated, user, login, logout, loading } = useAuth();

  if (loading) {
    return <div className="auth-loading">Loading...</div>;
  }

  if (isAuthenticated && user) {
    return (
      <div className="auth-user">
        <span className="user-name">{user.name || user.preferred_username || user.email || user.sub}</span>
        <button onClick={logout} className="btn btn-secondary btn-sm" disabled={loading}>
          Logout
        </button>
      </div>
    );
  }

  return (
    <button onClick={login} className="btn btn-primary" disabled={loading}>
      Login with Keycloak
    </button>
  );
}
