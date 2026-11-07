import { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function Callback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { handleCallback } = useAuth();

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const error = searchParams.get('error');
    const errorDescription = searchParams.get('error_description');

    if (error) {
      console.error('OAuth error:', error, errorDescription);
      navigate('/', { replace: true });
      return;
    }

    if (code && state) {
      handleCallback(code, state);
      navigate('/', { replace: true });
    } else {
      navigate('/', { replace: true });
    }
  }, [searchParams, handleCallback, navigate]);

  return (
    <div className="callback-container">
      <div className="callback-content">
        <div className="spinner"></div>
        <p>Completing login...</p>
      </div>
    </div>
  );
}
