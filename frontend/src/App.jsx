import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import WelcomePage from "./pages/WelcomePage";
import Dashboard from "./pages/DashboardPage";
import AnalyticsDashboard from "./pages/AnalyticsDashboard";
import ErrorBoundary from "./components/ErrorBoundary";

// Route wrapper for protected pages
const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center h-screen bg-gray-50">
    <div className="text-center">
      <div className="w-12 h-12 border-4 border-teal-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
      <p className="text-gray-600">Loading...</p>
    </div>
  </div>;
  return user ? children : <Navigate to="/login" replace />;
};

// Login route - always show login page, no auto-redirect
const LoginRoute = ({ children }) => {
  const { loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center h-screen bg-gray-50">
    <div className="text-center">
      <div className="w-12 h-12 border-4 border-teal-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
      <p className="text-gray-600">Loading...</p>
    </div>
  </div>;
  // Always show login page - let user decide to login or signup
  return children;
};

// Welcome route - protected, but checks if database is configured
const WelcomeRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center h-screen bg-gray-50">
    <div className="text-center">
      <div className="w-12 h-12 border-4 border-teal-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
      <p className="text-gray-600">Loading...</p>
    </div>
  </div>;
  if (!user) return <Navigate to="/login" replace />;
  
  // If user already has database configured, go to analytics dashboard
  const savedConfig = localStorage.getItem("dbConfig");
  if (savedConfig) {
    try {
      const config = JSON.parse(savedConfig);
      if (config.connectionString) {
        return <Navigate to="/dashboard" replace />; // Analytics Dashboard (default)
      }
    } catch (e) {
      // Invalid config, show welcome page
    }
  }
  return children;
};

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={<LandingPage />}
          />
          <Route
            path="/login"
            element={
              <LoginRoute>
                <LoginPage />
              </LoginRoute>
            }
          />
          <Route
            path="/welcome"
            element={
              <WelcomeRoute>
                <WelcomePage />
              </WelcomeRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <AnalyticsDashboard activeView="analytics" onChatClick={() => window.location.href = '/chat'} />
              </PrivateRoute>
            }
          />
          <Route
            path="/chat"
            element={
              <PrivateRoute>
                <ErrorBoundary>
                  <Dashboard />
                </ErrorBoundary>
              </PrivateRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
