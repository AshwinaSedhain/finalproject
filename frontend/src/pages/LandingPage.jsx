import React from "react";
import { useNavigate } from "react-router-dom";
import {
  BarChart3,
  ArrowRight,
  TrendingUp,
  Check
} from "lucide-react";

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="h-screen w-screen overflow-hidden bg-white flex flex-col">
      {/* Navigation Bar */}
      <nav className="w-full px-6 lg:px-12 py-4 flex items-center justify-between bg-white border-b border-gray-100 z-50">
        {/* Logo */}
        <button 
          onClick={() => navigate('/')}
          className="flex items-center gap-3 hover:opacity-80 transition-opacity cursor-pointer"
        >
          <div className="w-10 h-10 bg-gradient-to-br from-teal-600 to-cyan-600 rounded-lg flex items-center justify-center">
            <BarChart3 className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold text-gray-900">InsightAI</span>
        </button>

        {/* Navigation Links - Login and Signup Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/login?mode=login")}
            className="text-gray-700 hover:text-teal-600 transition-colors text-sm font-semibold px-4 py-2"
          >
            LOGIN
          </button>
          <button
            onClick={() => navigate("/login?mode=signup")}
            className="bg-teal-600 text-white px-5 py-2 rounded-lg hover:bg-teal-700 transition-all text-sm font-semibold shadow-md"
          >
            SIGNUP
          </button>
        </div>
      </nav>

      {/* Hero Section - Non-scrollable */}
      <div className="flex-1 relative w-full overflow-hidden">
        {/* Gradient Background - Teal/Cyan */}
        <div className="absolute inset-0 bg-gradient-to-br from-teal-600 via-teal-500 to-cyan-600">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-teal-500/50 to-white"></div>
          {/* Abstract shapes */}
          <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-teal-400/20 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-cyan-400/20 rounded-full blur-3xl"></div>
        </div>

        {/* Content */}
        <div className="relative z-10 h-full flex items-center">
          <div className="max-w-7xl mx-auto px-6 lg:px-12 w-full">
            <div className="grid lg:grid-cols-2 gap-12 items-center h-full">
              
              {/* Left Column - Hero Content */}
              <div className="text-white space-y-6">
                {/* Headline */}
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight">
                  <span className="block">Mass People</span>
                  <span className="block">Oriented Software</span>
                </h1>

                {/* Description */}
                <p className="text-lg lg:text-xl text-white/90 leading-relaxed max-w-xl">
                  Transform your business data into actionable insights with our AI-powered analytics platform. 
                  Query your database in plain English and get instant, beautiful visualizations—no coding required.
                </p>

                {/* CTA Button */}
                <div className="pt-4">
                  <button
                    onClick={() => navigate("/login")}
                    className="bg-white text-teal-600 px-8 py-4 rounded-lg hover:bg-gray-50 transition-all font-bold text-base border-2 border-white flex items-center gap-2 shadow-lg"
                  >
                    GET STARTED
                    <ArrowRight className="w-5 h-5" />
                  </button>
                </div>

                {/* Trust Indicators */}
                <div className="flex flex-wrap items-center gap-6 pt-4">
                  <div className="flex items-center gap-2 text-white/90">
                    <Check className="w-4 h-4 text-white" />
                    <span className="text-sm">No credit card required</span>
                  </div>
                  <div className="flex items-center gap-2 text-white/90">
                    <Check className="w-4 h-4 text-white" />
                    <span className="text-sm">Setup in minutes</span>
                  </div>
                  <div className="flex items-center gap-2 text-white/90">
                    <Check className="w-4 h-4 text-white" />
                    <span className="text-sm">Free to start</span>
                  </div>
                </div>
              </div>

              {/* Right Column - InsightAI Dashboard Preview */}
              <div className="relative hidden lg:block">
                <div className="relative">
                  {/* Laptop Frame */}
                  <div className="relative bg-gray-300 rounded-t-2xl p-2 shadow-2xl">
                    {/* Laptop Screen */}
                    <div className="bg-white rounded-lg overflow-hidden shadow-inner">
                      {/* Dashboard Header */}
                      <div className="bg-gray-50 border-b border-gray-200 px-4 py-2 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-teal-600 rounded-full flex items-center justify-center">
                            <BarChart3 className="w-4 h-4 text-white" />
                          </div>
                          <span className="text-sm font-semibold text-gray-900">InsightAI Dashboard</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                          <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                          <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                        </div>
                      </div>

                      {/* Dashboard Content */}
                      <div className="p-4 bg-white">
                        {/* Line Chart Area */}
                        <div className="mb-4 bg-gradient-to-br from-teal-50 to-cyan-50 rounded-lg border border-gray-200 p-4">
                          <div className="flex items-center justify-between mb-3">
                            <div className="text-xs font-semibold text-gray-900">Revenue Trends</div>
                            <TrendingUp className="w-4 h-4 text-teal-600" />
                          </div>
                          {/* Line Chart Visualization */}
                          <div className="relative h-32">
                            <svg className="w-full h-full" viewBox="0 0 300 100" preserveAspectRatio="none">
                              {/* Grid lines */}
                              <line x1="0" y1="80" x2="300" y2="80" stroke="#e5e7eb" strokeWidth="1" />
                              <line x1="0" y1="60" x2="300" y2="60" stroke="#e5e7eb" strokeWidth="1" />
                              <line x1="0" y1="40" x2="300" y2="40" stroke="#e5e7eb" strokeWidth="1" />
                              <line x1="0" y1="20" x2="300" y2="20" stroke="#e5e7eb" strokeWidth="1" />
                              
                              {/* Teal line (top) */}
                              <polyline
                                points="0,70 30,65 60,60 90,55 120,50 150,45 180,40 210,35 240,30 270,25 300,20"
                                fill="none"
                                stroke="#14b8a6"
                                strokeWidth="2.5"
                                strokeLinecap="round"
                              />
                              
                              {/* Green/Cyan line (bottom) */}
                              <polyline
                                points="0,85 30,80 60,75 90,70 120,65 150,60 180,55 210,50 240,45 270,40 300,35"
                                fill="none"
                                stroke="#10b981"
                                strokeWidth="2.5"
                                strokeLinecap="round"
                              />
                              
                              {/* Data points */}
                              <circle cx="0" cy="70" r="3" fill="#14b8a6" />
                              <circle cx="150" cy="45" r="3" fill="#14b8a6" />
                              <circle cx="300" cy="20" r="3" fill="#14b8a6" />
                              <circle cx="0" cy="85" r="3" fill="#10b981" />
                              <circle cx="150" cy="60" r="3" fill="#10b981" />
                              <circle cx="300" cy="35" r="3" fill="#10b981" />
                            </svg>
                            
                            {/* Y-axis labels */}
                            <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-gray-600">
                              <span>$2.4M</span>
                              <span>$1.8M</span>
                              <span>$1.2M</span>
                            </div>
                          </div>
                        </div>

                        {/* Metrics Grid */}
                        <div className="grid grid-cols-3 gap-3 mb-4">
                          <div className="bg-teal-50 rounded-lg p-3 border border-teal-100">
                            <div className="text-xs text-gray-600 mb-1">Total Sales</div>
                            <div className="text-base font-bold text-gray-900">$2.4M</div>
                            <div className="text-xs text-teal-600 mt-1 flex items-center gap-1">
                              <TrendingUp className="w-3 h-3" />
                              +12.5%
                            </div>
                          </div>
                          <div className="bg-cyan-50 rounded-lg p-3 border border-cyan-100">
                            <div className="text-xs text-gray-600 mb-1">Users</div>
                            <div className="text-base font-bold text-gray-900">1.2K</div>
                            <div className="text-xs text-cyan-600 mt-1 flex items-center gap-1">
                              <TrendingUp className="w-3 h-3" />
                              +8.2%
                            </div>
                          </div>
                          <div className="bg-teal-50 rounded-lg p-3 border border-teal-100">
                            <div className="text-xs text-gray-600 mb-1">Growth</div>
                            <div className="text-base font-bold text-gray-900">24%</div>
                            <div className="text-xs text-teal-600 mt-1 flex items-center gap-1">
                              <TrendingUp className="w-3 h-3" />
                              +5.1%
                            </div>
                          </div>
                        </div>

                        {/* Quick Stats */}
                        <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-gray-600">Active Queries</span>
                            <span className="text-gray-900 font-semibold">1,234</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  {/* Laptop Base */}
                  <div className="h-2 bg-gray-400 rounded-b-lg mx-4"></div>
                  <div className="h-1 bg-gray-500 rounded-lg mx-8"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;