import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@/contexts/theme-context';
import { AuthProvider, useAuth } from '@/contexts/auth-context';
import { Navbar } from '@/components/layout/navbar';
import Dashboard from '@/pages/dashboard';
import Analytics from '@/pages/analytics';
import Settings from '@/pages/settings';
import Login from '@/pages/login';
import { TestComponent } from '@/components/TestComponent';

// Protected route
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// Main layout
function Layout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-background">
      {isAuthenticated && <Navbar />}
      <main className={isAuthenticated ? 'pt-0' : ''}>
        {children}
      </main>
    </div>
  );
}

// App router
function AppRouter() {
  return (
    <Router>
      <Layout>
        <Routes>
          {/* Test route */}
          <Route path="/test" element={<TestComponent />} />
          
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected routes */}
          <Route path="/" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          
          {/* Analytics */}
          <Route path="/analytics" element={
            <ProtectedRoute>
              <Analytics />
            </ProtectedRoute>
          } />
          
          {/* Settings */}
          <Route path="/settings" element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          } />
          
          {/* Fallback route */}
          <Route path="*" element={
            <div className="container mx-auto p-6">
              <div className="text-center">
                <h1 className="text-3xl font-bold mb-4">404 - Page Not Found</h1>
                <p className="text-muted-foreground mb-4">
                  The page you're looking for doesn't exist.
                </p>
                <a href="/" className="text-primary hover:underline">
                  Go back to Dashboard
                </a>
              </div>
            </div>
          } />
        </Routes>
      </Layout>
    </Router>
  );
}

// App component
function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="yolo-ui-theme">
      <AuthProvider>
        <AppRouter />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
