import React, { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { QueryProvider } from './contexts/QueryProvider';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import ErrorBoundary from './components/common/ErrorBoundary';
import SignUp from './components/SignUp';
import Login from './components/Login';
import ProtectedRoute from './components/ProtectedRoute';

// Lazy load heavy components
const Dashboard = lazy(() => import('./components/Dashboard'));

// Loading component
const PageLoader = () => (
  <div style={{
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    background: 'var(--dark-bg)',
    color: 'var(--dark-text)'
  }}>
    <div style={{ textAlign: 'center' }}>
      <div className="spinner" style={{
        width: '50px',
        height: '50px',
        borderRadius: '50%',
        border: '4px solid rgba(79, 70, 229, 0.2)',
        borderTopColor: 'var(--primary-color)',
        animation: 'spin 1s linear infinite',
        margin: '0 auto 20px'
      }}></div>
      <p>Loading...</p>
    </div>
  </div>
);

function App() {
  return (
    <ErrorBoundary>
      <QueryProvider>
        <ThemeProvider>
          <AuthProvider>
            <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<SignUp />} />
                <Route
                  path="/dashboard/*"
                  element={
                    <ProtectedRoute>
                      <Suspense fallback={<PageLoader />}>
                        <Dashboard />
                      </Suspense>
                    </ProtectedRoute>
                  }
                />
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </Router>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 3000,
                style: {
                  background: 'var(--dark-card-bg)',
                  color: 'var(--dark-text)',
                },
                success: {
                  iconTheme: {
                    primary: 'var(--success-color)',
                    secondary: 'white',
                  },
                },
                error: {
                  iconTheme: {
                    primary: 'var(--error-color)',
                    secondary: 'white',
                  },
                },
              }}
            />
          </AuthProvider>
        </ThemeProvider>
      </QueryProvider>
    </ErrorBoundary>
  );
}

export default App;
