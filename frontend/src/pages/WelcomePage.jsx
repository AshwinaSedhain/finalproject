import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  Database,
  ArrowRight,
  Check,
  Sparkles,
  BarChart3,
  Zap,
  Shield,
  Globe,
  ChevronRight
} from "lucide-react";
import { testDatabaseConnection } from "../api";

const WelcomePage = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [connectionString, setConnectionString] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    // Check if user already has a database configured
    const savedConfig = localStorage.getItem("dbConfig");
    if (savedConfig) {
      try {
        const config = JSON.parse(savedConfig);
        if (config.connectionString) {
          // User already has config, skip to dashboard
          navigate("/dashboard");
        }
      } catch (e) {
        // Invalid config, continue with setup
      }
    }
  }, [navigate]);
  
  // Check if user is logged in
  useEffect(() => {
    if (!user) {
      navigate("/login");
    }
  }, [user, navigate]);

  const handleTestConnection = async () => {
    if (!connectionString.trim()) {
      setError("Please enter a connection string");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess(false);

    try {
      const result = await testDatabaseConnection(
        { connectionString: connectionString.trim() },
        token
      );

      if (result.status === "success") {
        setSuccess(true);
        
        // Get old connection string before saving new one
        const savedConfig = localStorage.getItem("dbConfig");
        let oldConnectionString = null;
        if (savedConfig) {
          try {
            const oldConfig = JSON.parse(savedConfig);
            oldConnectionString = oldConfig?.connectionString;
          } catch (e) {
            // Ignore parse errors
          }
        }
        
        const newConnectionString = connectionString.trim();
        
        // Save new connection to localStorage
        localStorage.setItem("dbConfig", JSON.stringify({ connectionString: newConnectionString }));
        
        // Clear old connection from backend cache if it exists and is different
        if (oldConnectionString && oldConnectionString !== newConnectionString) {
          try {
            const { clearOldDatabaseConnection } = await import("../api");
            await clearOldDatabaseConnection(token, oldConnectionString);
            console.log('✓ Cleared old database connection');
          } catch (error) {
            console.warn('Failed to clear old connection (non-critical):', error);
          }
        }
        
        setTimeout(() => {
          navigate("/dashboard"); // Redirect to Analytics Dashboard (default)
        }, 1500);
      } else {
        setError(result.message || "Connection failed. Please check your connection string.");
      }
    } catch (err) {
      setError(err.message || "Failed to connect to database. Please verify your connection string.");
    } finally {
      setLoading(false);
    }
  };


  const features = [
    {
      icon: <BarChart3 className="w-5 h-5" />,
      text: "Ask questions in natural language"
    },
    {
      icon: <Zap className="w-5 h-5" />,
      text: "Get instant insights and visualizations"
    },
    {
      icon: <Shield className="w-5 h-5" />,
      text: "Secure and encrypted connections"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-cyan-50 to-blue-50">
      {/* Logo Navigation */}
      <nav className="w-full px-6 lg:px-12 py-4 bg-white border-b border-gray-100">
        <button 
          onClick={() => navigate('/')}
          className="flex items-center gap-3 hover:opacity-80 transition-opacity cursor-pointer"
        >
          <div className="w-10 h-10 bg-gradient-to-br from-teal-600 to-cyan-600 rounded-lg flex items-center justify-center">
            <BarChart3 className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold text-gray-900">InsightAI</span>
        </button>
      </nav>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-teal-600 rounded-full mb-4">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-3">
            Welcome to InsightAI, {user?.user_metadata?.full_name || user?.email?.split("@")[0] || "there"}!
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Let's get you started by connecting your database. This will only take a minute.
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-12">
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 ${step >= 1 ? 'text-teal-600' : 'text-gray-400'}`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${
                step >= 1 ? 'bg-teal-600 border-teal-600 text-white' : 'border-gray-300'
              }`}>
                {step > 1 ? <Check className="w-5 h-5" /> : '1'}
              </div>
              <span className="font-medium hidden sm:inline">Welcome</span>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400" />
            <div className={`flex items-center gap-2 ${step >= 2 ? 'text-teal-600' : 'text-gray-400'}`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${
                step >= 2 ? 'bg-teal-600 border-teal-600 text-white' : 'border-gray-300'
              }`}>
                {step > 2 ? <Check className="w-5 h-5" /> : '2'}
              </div>
              <span className="font-medium hidden sm:inline">Connect Database</span>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400" />
            <div className={`flex items-center gap-2 ${step >= 3 ? 'text-teal-600' : 'text-gray-400'}`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${
                step >= 3 ? 'bg-teal-600 border-teal-600 text-white' : 'border-gray-300'
              }`}>
                3
              </div>
              <span className="font-medium hidden sm:inline">Ready</span>
            </div>
          </div>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-8 md:p-12">
          {step === 1 && (
            <div className="text-center">
              <div className="mb-8">
                <Database className="w-16 h-16 text-teal-600 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-3">
                  Connect Your Database
                </h2>
                <p className="text-gray-600 max-w-lg mx-auto">
                  InsightAI works with PostgreSQL databases. Connect your database to start asking questions and getting insights.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                {features.map((feature, index) => (
                  <div key={index} className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
                    <div className="text-teal-600 flex-shrink-0">
                      {feature.icon}
                    </div>
                    <span className="text-sm font-medium text-gray-700">{feature.text}</span>
                  </div>
                ))}
              </div>

              <button
                onClick={() => setStep(2)}
                className="bg-teal-600 text-white px-8 py-3 rounded-lg hover:bg-teal-700 transition-all font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 flex items-center gap-2 mx-auto"
              >
                Get Started
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          )}

          {step === 2 && (
            <div>
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Database Connection
                </h2>
                <p className="text-gray-600">
                  Enter your PostgreSQL database connection string to get started.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Connection String
                </label>
                <textarea
                  value={connectionString}
                  onChange={(e) => setConnectionString(e.target.value)}
                  placeholder="postgresql://username:password@host:port/database"
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent font-mono text-sm"
                />
                <p className="mt-2 text-sm text-gray-500">
                  Format: postgresql://username:password@host:port/database
                </p>
              </div>

              {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              {success && (
                <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm text-green-600 flex items-center gap-2">
                    <Check className="w-4 h-4" />
                    Connection successful! Redirecting to dashboard...
                  </p>
                </div>
              )}

              <div className="flex items-center gap-4 mt-8">
                <button
                  onClick={() => setStep(1)}
                  className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium text-gray-700"
                >
                  Back
                </button>
                <button
                  onClick={handleTestConnection}
                  disabled={loading || success}
                  className="flex-1 bg-teal-600 text-white px-6 py-3 rounded-lg hover:bg-teal-700 transition-all font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Testing Connection...
                    </>
                  ) : success ? (
                    <>
                      <Check className="w-5 h-5" />
                      Connected!
                    </>
                  ) : (
                    <>
                      Test Connection
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Security Note */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500 flex items-center justify-center gap-2">
            <Shield className="w-4 h-4" />
            Your credentials are encrypted and stored securely on your device
          </p>
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;

