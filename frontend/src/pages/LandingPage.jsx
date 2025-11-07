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
          <div className="w-12 h-12 bg-gradient-to-br from-blue-700 to-blue-800 rounded-xl flex items-center justify-center shadow-xl ring-2 ring-blue-300/30">
            <BarChart3 className="w-7 h-7 text-white" />
          </div>
          <span className="text-2xl font-black text-slate-900 tracking-tight">InsightAI</span>
        </button>

        {/* Navigation Links - Login and Signup Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/login?mode=login")}
            className="text-slate-700 hover:text-blue-600 transition-colors text-sm font-semibold px-4 py-2"
          >
            LOGIN
          </button>
          <button
            onClick={() => navigate("/login?mode=signup")}
            className="bg-blue-500 text-white px-6 py-2.5 rounded-lg hover:bg-blue-600 transition-all text-sm font-bold shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          >
            SIGNUP
          </button>
        </div>
      </nav>

      {/* Hero Section - Non-scrollable */}
      <div className="flex-1 relative w-full overflow-hidden">
        {/* Premium Gradient Background - Dark Blue with Blue Accents */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900 via-blue-800 to-blue-950">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-blue-800/40 to-white/95"></div>
          {/* Animated abstract shapes - Blue accent */}
          <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-blue-400/25 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-0 left-0 w-[700px] h-[700px] bg-cyan-400/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
          <div className="absolute top-1/2 right-1/4 w-[600px] h-[600px] bg-blue-400/15 rounded-full blur-3xl"></div>
          {/* Mesh gradient overlay for premium feel */}
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(96,165,250,0.2),transparent_50%)]"></div>
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(34,211,238,0.3),transparent_50%)]"></div>
        </div>

        {/* Content */}
        <div className="relative z-10 h-full flex items-center">
          <div className="max-w-7xl mx-auto px-6 lg:px-12 w-full">
            <div className="grid lg:grid-cols-2 gap-12 items-center h-full">
              
              {/* Left Column - Hero Content */}
              <div className="text-white space-y-8">
                {/* Headline with blue accent underline */}
                <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black leading-tight text-white">
                  <span className="block">Ask Your Data</span>
                  <span className="block">Get Instant</span>
                  <span className="block relative mt-2">
                    Insights
                    <span className="absolute bottom-0 left-0 w-full h-1.5 bg-blue-400/60 rounded-full"></span>
                  </span>
                </h1>

                {/* Description with better typography - Improved contrast */}
                <p className="text-xl lg:text-2xl text-white leading-relaxed max-w-xl font-light">
                  Transform your business data into <span className="font-semibold text-blue-300">actionable insights</span> with our AI-powered analytics platform. 
                  Query your database in <span className="font-semibold text-cyan-300">plain English</span> and get instant, beautiful visualizations—no coding required.
                </p>

                {/* Premium CTA Button with blue accent */}
                <div className="pt-6">
                  <button
                    onClick={() => navigate("/login")}
                    className="group relative bg-blue-500 text-white px-10 py-5 rounded-xl hover:bg-blue-600 transition-all font-bold text-lg border-2 border-blue-400 flex items-center gap-3 shadow-2xl hover:shadow-[0_20px_50px_rgba(59,130,246,0.4)] transform hover:-translate-y-1 hover:scale-105 overflow-hidden"
                  >
                    <span className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-cyan-400/20 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                    <span className="relative z-10">GET STARTED</span>
                    <ArrowRight className="w-6 h-6 relative z-10 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>

                {/* Trust Indicators with improved contrast - Much darker background for visibility */}
                <div className="flex flex-wrap items-center gap-8 pt-6">
                  <div className="flex items-center gap-3 bg-blue-900/80 backdrop-blur-md px-4 py-2 rounded-full border-2 border-blue-400 shadow-xl">
                    <div className="w-5 h-5 bg-blue-400 rounded-full flex items-center justify-center shadow-md ring-2 ring-blue-300">
                      <Check className="w-3 h-3 text-white font-bold" />
                    </div>
                    <span className="text-sm font-bold text-white [text-shadow:0_2px_4px_rgba(0,0,0,0.8),0_0_8px_rgba(255,255,255,0.3)]">No credit card required</span>
                  </div>
                  <div className="flex items-center gap-3 bg-blue-900/80 backdrop-blur-md px-4 py-2 rounded-full border-2 border-blue-400 shadow-xl">
                    <div className="w-5 h-5 bg-blue-400 rounded-full flex items-center justify-center shadow-md ring-2 ring-blue-300">
                      <Check className="w-3 h-3 text-white font-bold" />
                    </div>
                    <span className="text-sm font-bold text-white [text-shadow:0_2px_4px_rgba(0,0,0,0.8),0_0_8px_rgba(255,255,255,0.3)]">Setup in minutes</span>
                  </div>
                  <div className="flex items-center gap-3 bg-blue-900/80 backdrop-blur-md px-4 py-2 rounded-full border-2 border-blue-400 shadow-xl">
                    <div className="w-5 h-5 bg-blue-400 rounded-full flex items-center justify-center shadow-md ring-2 ring-blue-300">
                      <Check className="w-3 h-3 text-white font-bold" />
                    </div>
                    <span className="text-sm font-bold text-white [text-shadow:0_2px_4px_rgba(0,0,0,0.8),0_0_8px_rgba(255,255,255,0.3)]">Free to start</span>
                  </div>
                </div>
              </div>

              {/* Right Column - InsightAI Dashboard Preview with premium effects */}
              <div className="relative hidden lg:block">
                <div className="relative transform hover:scale-105 transition-transform duration-500">
                  {/* Glow effect behind laptop - Blue accent */}
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-cyan-500/20 rounded-3xl blur-2xl"></div>
                  
                  {/* Laptop Frame with premium styling */}
                  <div className="relative bg-gradient-to-b from-slate-400 to-slate-500 rounded-t-3xl p-3 shadow-2xl border border-slate-300/50">
                    {/* Laptop Screen with glassmorphism */}
                    <div className="bg-white rounded-xl overflow-hidden shadow-2xl border-2 border-white/50 backdrop-blur-sm">
                      {/* Dashboard Header with premium styling */}
                      <div className="bg-gradient-to-r from-slate-50 to-blue-50/30 border-b border-slate-200/50 px-5 py-3 flex items-center justify-between backdrop-blur-sm">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-700 to-blue-800 rounded-xl flex items-center justify-center shadow-lg ring-2 ring-blue-300/30">
                            <BarChart3 className="w-5 h-5 text-white" />
                          </div>
                          <span className="text-sm font-bold text-slate-900 tracking-tight">InsightAI Dashboard</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                          <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                          <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                        </div>
                      </div>

                      {/* Dashboard Content with premium styling */}
                      <div className="p-5 bg-gradient-to-br from-white to-slate-50/50">
                        {/* Line Chart Area with enhanced design - Blue theme */}
                        <div className="mb-5 bg-gradient-to-br from-blue-50 via-cyan-50/20 to-white rounded-xl border-2 border-blue-100/50 p-5 shadow-lg backdrop-blur-sm relative overflow-hidden">
                          {/* Decorative gradient overlay - Blue accent */}
                          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-300/20 to-transparent rounded-full blur-2xl"></div>
                          <div className="relative z-10">
                            <div className="flex items-center justify-between mb-4">
                              <div className="text-sm font-bold text-slate-900 tracking-tight">Revenue Trends</div>
                              <div className="flex items-center gap-2 bg-blue-400/90 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-blue-300">
                                <TrendingUp className="w-4 h-4 text-white" />
                                <span className="text-xs font-semibold text-white">+24.5%</span>
                              </div>
                            </div>
                            {/* Line Chart Visualization with premium styling */}
                            <div className="relative h-36">
                              <svg className="w-full h-full" viewBox="0 0 300 100" preserveAspectRatio="none">
                              {/* Grid lines with subtle styling */}
                              <line x1="0" y1="80" x2="300" y2="80" stroke="#e2e8f0" strokeWidth="1" />
                              <line x1="0" y1="60" x2="300" y2="60" stroke="#e2e8f0" strokeWidth="1" />
                              <line x1="0" y1="40" x2="300" y2="40" stroke="#e2e8f0" strokeWidth="1" />
                              <line x1="0" y1="20" x2="300" y2="20" stroke="#e2e8f0" strokeWidth="1" />
                              
                              {/* Gradient definitions for lines - Blue and Cyan */}
                              <defs>
                                <linearGradient id="blueGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                  <stop offset="0%" stopColor="#3b82f6" />
                                  <stop offset="100%" stopColor="#2563eb" />
                                </linearGradient>
                                <linearGradient id="cyanGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                  <stop offset="0%" stopColor="#06b6d4" />
                                  <stop offset="100%" stopColor="#0891b2" />
                                </linearGradient>
                              </defs>
                              
                              {/* Blue line (top) - Primary metric with gradient */}
                              <polyline
                                points="0,70 30,65 60,60 90,55 120,50 150,45 180,40 210,35 240,30 270,25 300,20"
                                fill="none"
                                stroke="url(#blueGradient)"
                                strokeWidth="3"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                              />
                              
                              {/* Cyan line (bottom) - Secondary metric with gradient */}
                              <polyline
                                points="0,85 30,80 60,75 90,70 120,65 150,60 180,55 210,50 240,45 270,40 300,35"
                                fill="none"
                                stroke="url(#cyanGradient)"
                                strokeWidth="3"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                              />
                              
                              {/* Data points with glow effect */}
                              <circle cx="0" cy="70" r="4" fill="#2563eb" className="drop-shadow-lg" />
                              <circle cx="150" cy="45" r="4" fill="#2563eb" className="drop-shadow-lg" />
                              <circle cx="300" cy="20" r="4" fill="#2563eb" className="drop-shadow-lg" />
                              <circle cx="0" cy="85" r="4" fill="#0891b2" className="drop-shadow-lg" />
                              <circle cx="150" cy="60" r="4" fill="#0891b2" className="drop-shadow-lg" />
                              <circle cx="300" cy="35" r="4" fill="#0891b2" className="drop-shadow-lg" />
                            </svg>
                            
                              {/* Y-axis labels with better styling */}
                              <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-xs font-semibold text-slate-700">
                                <span>$2.4M</span>
                                <span>$1.8M</span>
                                <span>$1.2M</span>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Metrics Grid with premium card design - Blue theme */}
                        <div className="grid grid-cols-3 gap-4 mb-5">
                          <div className="group relative bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-xl p-4 border-2 border-blue-200/50 shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 overflow-hidden">
                            <div className="absolute top-0 right-0 w-20 h-20 bg-blue-300/20 rounded-full blur-2xl"></div>
                            <div className="relative z-10">
                              <div className="text-xs font-semibold text-slate-600 mb-2 uppercase tracking-wide">Total Sales</div>
                              <div className="text-xl font-black text-slate-900 mb-2">$2.4M</div>
                              <div className="text-xs font-bold text-blue-700 flex items-center gap-1.5 bg-blue-100/50 px-2 py-1 rounded-md w-fit">
                                <TrendingUp className="w-3.5 h-3.5" />
                                +12.5%
                              </div>
                            </div>
                          </div>
                          <div className="group relative bg-gradient-to-br from-cyan-50 to-cyan-100/50 rounded-xl p-4 border-2 border-cyan-200/50 shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 overflow-hidden">
                            <div className="absolute top-0 right-0 w-20 h-20 bg-cyan-300/20 rounded-full blur-2xl"></div>
                            <div className="relative z-10">
                              <div className="text-xs font-semibold text-slate-600 mb-2 uppercase tracking-wide">Users</div>
                              <div className="text-xl font-black text-slate-900 mb-2">1.2K</div>
                              <div className="text-xs font-bold text-cyan-700 flex items-center gap-1.5 bg-cyan-100/50 px-2 py-1 rounded-md w-fit">
                                <TrendingUp className="w-3.5 h-3.5" />
                                +8.2%
                              </div>
                            </div>
                          </div>
                          <div className="group relative bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-xl p-4 border-2 border-blue-200/50 shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 overflow-hidden">
                            <div className="absolute top-0 right-0 w-20 h-20 bg-blue-300/20 rounded-full blur-2xl"></div>
                            <div className="relative z-10">
                              <div className="text-xs font-semibold text-slate-600 mb-2 uppercase tracking-wide">Growth</div>
                              <div className="text-xl font-black text-slate-900 mb-2">24%</div>
                              <div className="text-xs font-bold text-blue-700 flex items-center gap-1.5 bg-blue-100/50 px-2 py-1 rounded-md w-fit">
                                <TrendingUp className="w-3.5 h-3.5" />
                                +5.1%
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Quick Stats with premium design - Blue accent */}
                        <div className="bg-gradient-to-r from-slate-50 to-blue-50/30 rounded-xl p-4 border-2 border-blue-100/50 shadow-md backdrop-blur-sm">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-semibold text-slate-700">Active Queries</span>
                            <div className="flex items-center gap-2">
                              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                              <span className="text-lg font-black text-slate-900">1,234</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  {/* Laptop Base with premium styling */}
                  <div className="h-3 bg-gradient-to-b from-slate-400 to-slate-500 rounded-b-2xl mx-4 shadow-lg"></div>
                  <div className="h-1.5 bg-slate-600 rounded-lg mx-12 shadow-md"></div>
                  
                  {/* Floating particles effect - Blue accent */}
                  <div className="absolute -top-4 -right-4 w-3 h-3 bg-blue-400 rounded-full animate-pulse blur-sm"></div>
                  <div className="absolute -bottom-4 -left-4 w-2 h-2 bg-cyan-400 rounded-full animate-pulse blur-sm" style={{ animationDelay: '0.5s' }}></div>
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