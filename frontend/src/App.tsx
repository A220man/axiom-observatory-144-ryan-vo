import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { BenchmarkForm } from './components/BenchmarkForm';
import { LoginButton } from './components/LoginButton';
import { Callback } from './components/Callback';
import { useAuth } from './hooks/useAuth';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div className="app-loading">Loading authentication...</div>;
  }
  
  return isAuthenticated ? <>{children}</> : <Navigate to="/" replace />;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div className="app-loading">Loading authentication...</div>;
  }
  
  return isAuthenticated ? <Navigate to="/benchmark" replace /> : <>{children}</>;
}

function AppContent() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Axiom Observatory</h1>
        <p className="subtitle">TokenSpeed Inference Benchmarking</p>
        <LoginButton />
      </header>
      <main className="app-main">
        <Routes>
          <Route path="/callback" element={<Callback />} />
          <Route 
            path="/" 
            element={
              <PublicRoute>
                <div className="landing-page">
                  <h2>Welcome to Axiom Observatory</h2>
                  <p>TokenSpeed Inference Benchmarking Platform</p>
                  <p>Please log in to run benchmarks.</p>
                </div>
              </PublicRoute>
            } 
          />
          <Route 
            path="/benchmark" 
            element={
              <ProtectedRoute>
                <BenchmarkForm />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </main>
      <footer className="app-footer">
        <p>Axiom Observatory &copy; 2024 Ryan Vo (ryandtvo@gmail.com)</p>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
