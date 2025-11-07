import React, { useState, useEffect } from "react";
import { useNavigate, Link, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  Loader2,
  BarChart3,
  Mail,
  Lock,
  User,
  Eye,
  EyeOff,
  CheckCircle2,
  AlertCircle,
  ArrowLeft
} from "lucide-react";

const LoginPage = () => {
  const { login, signup } = useAuth();
  const [searchParams] = useSearchParams();
  const mode = searchParams.get('mode');
  const [isLogin, setIsLogin] = useState(mode === 'signup' ? false : true);
  
  // Update mode when URL parameter changes
  useEffect(() => {
    if (mode === 'signup') {
      setIsLogin(false);
    } else if (mode === 'login') {
      setIsLogin(true);
    }
  }, [mode]);
  const [formData, setFormData] = useState({ email: "", password: "", name: "" });
  const [loading, setLoading] = useState(false);
  const [authMessage, setAuthMessage] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }
    
    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }
    
    if (!isLogin && !formData.name) {
      newErrors.name = "Name is required";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setAuthMessage("");
    setSuccess(false);
    setErrors({});

    try {
      if (isLogin) {
        const user = await login(formData.email, formData.password);
        if (user) {
          setSuccess(true);
          // Check if database is configured
          const savedConfig = localStorage.getItem("dbConfig");
          if (savedConfig) {
            try {
              const config = JSON.parse(savedConfig);
              if (config.connectionString) {
                setTimeout(() => {
                  navigate("/dashboard"); // Go to Analytics Dashboard
                }, 500);
                return;
              }
            } catch (e) {
              // Invalid config
            }
          }
          setTimeout(() => {
            navigate("/welcome"); // Go to database setup
          }, 500);
        }
      } else {
        const result = await signup(
          formData.email,
          formData.password,
          formData.name
        );

        // signup returns { user, needsConfirmation } or throws error
        if (result.needsConfirmation) {
          setSuccess(true);
          setAuthMessage(
            `Signup successful! Please check your email (${formData.email}) to confirm your account before logging in.`
          );
          setTimeout(() => {
            setIsLogin(true);
            setFormData({ ...formData, password: "" });
            setSuccess(false);
          }, 3000);
        } else if (result.user) {
          setSuccess(true);
          setTimeout(() => {
            navigate("/welcome");
          }, 500);
        }
      }
    } catch (error) {
      setAuthMessage(error.message || "An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSubmit(e);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-blue-950 flex">
      {/* Left side - Visual/Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-900 via-blue-800 to-blue-950 relative overflow-hidden">
        {/* Decorative elements - Blue accents */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-400/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-cyan-400/15 rounded-full blur-3xl"></div>
        
        <div className="relative z-10 flex flex-col justify-center px-16 py-12 text-white">
          {/* Back to home button */}
          <Link
            to="/"
            className="absolute top-8 left-8 flex items-center gap-2 text-white/90 hover:text-blue-300 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm font-medium">Back to home</span>
          </Link>

          {/* Logo */}
          <button 
            onClick={() => navigate('/')}
            className="flex items-center gap-3 mb-16 hover:opacity-80 transition-opacity cursor-pointer"
          >
            <div className="w-12 h-12 bg-blue-900 rounded-xl flex items-center justify-center border-2 border-blue-400/30 shadow-xl">
              <BarChart3 className="w-7 h-7 text-blue-400" />
            </div>
            <span className="text-3xl font-bold text-white">InsightAI</span>
          </button>

          {/* Content */}
          <div className="space-y-8 max-w-md">
            <div>
              <h1 className="text-5xl font-bold leading-tight mb-4">
                {isLogin ? "Welcome Back" : "Join InsightAI"}
              </h1>
              <p className="text-xl text-white/90 leading-relaxed">
                {isLogin
                  ? "Sign in to continue analyzing your data with AI-powered insights."
                  : "Start transforming your data into actionable insights today."}
              </p>
            </div>

            {/* Feature highlights */}
            <div className="space-y-4 pt-4">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-blue-400 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-md">
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                </div>
                <div>
                  <p className="font-medium text-white">AI-Powered Analysis</p>
                  <p className="text-sm text-white/80">Natural language queries with instant results</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-blue-400 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-md">
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                </div>
                <div>
                  <p className="font-medium text-white">Secure & Private</p>
                  <p className="text-sm text-white/80">Enterprise-grade security for your data</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-blue-400 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-md">
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                </div>
                <div>
                  <p className="font-medium text-white">Beautiful Visualizations</p>
                  <p className="text-sm text-white/80">Interactive charts and reports</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Auth Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-8 lg:p-12 bg-white">
        <div className="w-full max-w-md">
          {/* Mobile back button */}
          <Link
            to="/"
            className="lg:hidden flex items-center gap-2 text-slate-600 hover:text-teal-700 transition-colors mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm font-medium">Back</span>
          </Link>

          {/* Mobile logo */}
          <button 
            onClick={() => navigate('/')}
            className="lg:hidden flex items-center gap-2 mb-8 hover:opacity-80 transition-opacity cursor-pointer"
          >
            <div className="w-10 h-10 bg-blue-800 rounded-xl flex items-center justify-center border-2 border-blue-400/30">
              <BarChart3 className="w-6 h-6 text-blue-400" />
            </div>
            <span className="text-2xl font-bold text-slate-900">InsightAI</span>
          </button>

          {/* Auth Card */}
          <div>
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                {isLogin ? "Sign in to your account" : "Create your account"}
              </h2>
              <p className="text-gray-600">
                {isLogin
                  ? "Enter your credentials to access your workspace"
                  : "Fill in your details to get started"}
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {!isLogin && (
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Full Name
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <User className="w-5 h-5 text-gray-400" />
                    </div>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => {
                        setFormData({ ...formData, name: e.target.value });
                        if (errors.name) setErrors({ ...errors, name: "" });
                      }}
                      onKeyPress={handleKeyPress}
                      placeholder="John Doe"
                      className={`w-full pl-12 pr-4 py-3 border rounded-lg focus:outline-none focus:ring-2 transition-all ${
                        errors.name
                          ? "border-red-300 focus:ring-red-500 focus:border-red-500"
                          : "border-gray-300 focus:ring-blue-400 focus:border-blue-400"
                      }`}
                    />
                  </div>
                  {errors.name && (
                    <p className="mt-1.5 text-sm text-red-600 flex items-center gap-1">
                      <AlertCircle className="w-4 h-4" />
                      {errors.name}
                    </p>
                  )}
                </div>
              )}

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Mail className="w-5 h-5 text-gray-400" />
                  </div>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => {
                      setFormData({ ...formData, email: e.target.value });
                      if (errors.email) setErrors({ ...errors, email: "" });
                    }}
                    onKeyPress={handleKeyPress}
                    placeholder="you@company.com"
                    className={`w-full pl-12 pr-4 py-3 border rounded-lg focus:outline-none focus:ring-2 transition-all ${
                      errors.email
                        ? "border-red-300 focus:ring-red-500 focus:border-red-500"
                        : "border-gray-300 focus:ring-yellow-400 focus:border-yellow-400"
                    }`}
                  />
                </div>
                {errors.email && (
                  <p className="mt-1.5 text-sm text-red-600 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {errors.email}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Lock className="w-5 h-5 text-gray-400" />
                  </div>
                  <input
                    type={showPassword ? "text" : "password"}
                    value={formData.password}
                    onChange={(e) => {
                      setFormData({ ...formData, password: e.target.value });
                      if (errors.password) setErrors({ ...errors, password: "" });
                    }}
                    onKeyPress={handleKeyPress}
                    placeholder="Enter your password"
                    className={`w-full pl-12 pr-12 py-3 border rounded-lg focus:outline-none focus:ring-2 transition-all ${
                      errors.password
                        ? "border-red-300 focus:ring-red-500 focus:border-red-500"
                        : "border-gray-300 focus:ring-yellow-400 focus:border-yellow-400"
                    }`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                {errors.password && (
                  <p className="mt-1.5 text-sm text-red-600 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {errors.password}
                  </p>
                )}
              </div>

              {authMessage && (
                <div
                  className={`p-4 rounded-lg flex items-start gap-3 ${
                    success
                      ? "bg-green-50 border border-green-200"
                      : "bg-red-50 border border-red-200"
                  }`}
                >
                  {success ? (
                    <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  )}
                  <p
                    className={`text-sm ${
                      success ? "text-green-700" : "text-red-700"
                    }`}
                  >
                    {authMessage}
                  </p>
                </div>
              )}

              <button
                type="submit"
                disabled={loading || success}
                className="w-full py-3.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-all disabled:bg-gray-400 disabled:cursor-not-allowed font-bold shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:transform-none flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    {isLogin ? "Signing in..." : "Creating account..."}
                  </>
                ) : success ? (
                  <>
                    <CheckCircle2 className="w-5 h-5" />
                    {isLogin ? "Success! Redirecting..." : "Account created!"}
                  </>
                ) : (
                  <>{isLogin ? "Sign In" : "Create Account"}</>
                )}
              </button>
            </form>

            <div className="mt-6 text-center">
              <button
                onClick={() => {
                  setIsLogin(!isLogin);
                  setAuthMessage("");
                  setErrors({});
                  setSuccess(false);
                }}
                className="text-sm text-gray-600 hover:text-blue-600 transition-colors"
              >
                {isLogin ? (
                  <>
                    Don't have an account?{" "}
                    <span className="font-semibold text-blue-600">Sign up for free</span>
                  </>
                ) : (
                  <>
                    Already have an account?{" "}
                    <span className="font-semibold text-blue-600">Sign in</span>
                  </>
                )}
              </button>
            </div>

            <div className="mt-8 pt-6 border-t border-gray-200">
              <p className="text-xs text-gray-500 text-center">
                By continuing, you agree to our{" "}
                <a href="#" className="text-blue-600 hover:underline">
                  Terms of Service
                </a>{" "}
                and{" "}
                <a href="#" className="text-blue-600 hover:underline">
                  Privacy Policy
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
