import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { 
  Database, 
  BarChart3, 
  Calendar,
  RefreshCw,
  AlertCircle
} from "lucide-react";
import Navbar from "../components/NavBar";
import DatabaseSetupModal from "../components/DatabaseSetupModal";
import { useNavigate } from "react-router-dom";
import Plot from "react-plotly.js";
import { getDashboardData } from "../api";

const AnalyticsDashboard = ({ activeView, onChatClick }) => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  
  const [dbConfig, setDbConfig] = useState(() => {
    try {
      const saved = localStorage.getItem("dbConfig");
      return saved ? JSON.parse(saved) : null;
    } catch { return null; }
  });

  useEffect(() => {
    if (dbConfig?.connectionString) {
      fetchDashboardData();
    }
  }, [dbConfig]);

  const handleSaveDbConfig = async (config) => {
    if (config && config.connectionString) {
      // Get old connection string before saving new one
      const oldConfig = dbConfig;
      const oldConnectionString = oldConfig?.connectionString;
      
      // Save new connection
      localStorage.setItem("dbConfig", JSON.stringify(config));
      setDbConfig(config);
      
      // Clear old connection from backend cache if it exists and is different
      if (oldConnectionString && oldConnectionString !== config.connectionString) {
        try {
          const { clearOldDatabaseConnection } = await import('../api');
          await clearOldDatabaseConnection(token, oldConnectionString);
          console.log('✓ Cleared old database connection');
        } catch (error) {
          console.warn('Failed to clear old connection (non-critical):', error);
        }
      }
      
      fetchDashboardData();
    }
  };

  const fetchDashboardData = async () => {
    if (!dbConfig?.connectionString) {
      setError("No database connection configured");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await getDashboardData(token, dbConfig.connectionString);
      setDashboardData(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
      console.error("Error fetching dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good Morning";
    if (hour < 18) return "Good Afternoon";
    return "Good Evening";
  };

  const getCurrentDate = () => {
    const date = new Date();
    const options = { year: 'numeric', month: 'short', day: 'numeric', weekday: 'long' };
    return date.toLocaleDateString('en-US', options);
  };

  const getStatusColor = (status) => {
    const colors = {
      'In Stock': 'bg-green-100 text-green-800',
      'Low Stock': 'bg-orange-100 text-orange-800',
      'Out of Stock': 'bg-purple-100 text-purple-800',
      'Critically Low': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (!dbConfig || !dbConfig.connectionString) {
    return <DatabaseSetupModal isOpen={true} onSave={handleSaveDbConfig} />;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-teal-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
          <p className="text-gray-900 font-semibold mb-2">Error loading dashboard</p>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Left Sidebar */}
      <div className="w-16 bg-teal-600 flex flex-col items-center py-6 gap-4">
        <button 
          className="p-3 rounded-lg bg-teal-700 hover:bg-teal-800 transition-colors"
          title="Analytics Dashboard"
        >
          <Database className="w-6 h-6 text-white" />
        </button>
        <button 
          onClick={() => navigate('/chat')}
          className="p-3 rounded-lg hover:bg-teal-700/50 transition-colors"
          title="Chat with Database"
        >
          <BarChart3 className="w-6 h-6 text-white" />
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200">
          <Navbar 
            activeView={activeView}
            onChatClick={() => navigate('/chat')}
          />
        </div>
        <div className="px-8 py-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {getGreeting()}, {user?.user_metadata?.full_name || user?.email?.split("@")[0] || "User"}
              </h1>
              <p className="text-gray-600 mt-1">
                Welcome to your {dashboardData?.businessType || 'Business'} inventory management system
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-gray-600">
                <Calendar className="w-5 h-5" />
                <span className="text-sm">{getCurrentDate()}</span>
              </div>
              <button
                onClick={fetchDashboardData}
                className="p-2 hover:bg-gray-100 rounded-lg"
                title="Refresh"
              >
                <RefreshCw className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          </div>

          {/* Chat with Database Button - Prominent */}
          <div className="mb-6 bg-gradient-to-r from-teal-50 to-cyan-50 rounded-xl p-6 border border-teal-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Ready to Explore Your Data?</h3>
                <p className="text-gray-600">Ask questions in natural language and get instant insights from your database.</p>
              </div>
              <button
                onClick={() => navigate('/chat')}
                className="px-8 py-4 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-all font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 flex items-center gap-3 whitespace-nowrap"
              >
                <BarChart3 className="w-6 h-6" />
                Chat with Database
                <span className="text-teal-200">→</span>
              </button>
            </div>
          </div>

          {/* Analytics Overview Cards */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Analytics Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {dashboardData?.metrics?.map((metric, index) => (
                <div
                  key={index}
                  className="bg-white rounded-xl p-6 shadow-lg border border-gray-200 relative overflow-hidden"
                  style={{
                    background: `linear-gradient(135deg, ${metric.color}15 0%, ${metric.color}05 100%)`,
                  }}
                >
                  <div className="absolute top-0 right-0 w-32 h-32 rounded-full opacity-10"
                    style={{ background: metric.color, transform: 'translate(30%, -30%)' }}
                  />
                  <div className="relative">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="p-2 rounded-lg" style={{ backgroundColor: `${metric.color}20` }}>
                        <span className="text-lg">{metric.icon || '📊'}</span>
                      </div>
                      <span className="text-sm font-medium text-gray-600">{metric.label}</span>
                    </div>
                    <div className="text-3xl font-bold text-gray-900">{metric.value}</div>
                    {metric.unit && <span className="text-sm text-gray-500 ml-2">{metric.unit}</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            {/* Top Selling Products Chart */}
            <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">Top Selling Products</h2>
              </div>
              <div className="p-6">
                {dashboardData?.topSellingChart ? (
                  <Plot
                    data={dashboardData.topSellingChart.data}
                    layout={{
                      ...dashboardData.topSellingChart.layout,
                      responsive: true,
                      autosize: true
                    }}
                    config={{ responsive: true, displayModeBar: false }}
                    style={{ width: '100%', height: '400px' }}
                  />
                ) : (
                  <div className="flex items-center justify-center h-96 text-gray-500">
                    <div className="text-center">
                      <p className="mb-2">No sales data available</p>
                      <p className="text-sm">Try asking questions in the chat interface to generate data.</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Right Sidebar - Charts and Lists */}
            <div className="space-y-6">
              {/* Pie Chart */}
              {dashboardData?.pieChart && (
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Overview</h3>
                  <Plot
                    data={dashboardData.pieChart.data}
                    layout={{
                      ...dashboardData.pieChart.layout,
                      height: 300,
                      showlegend: true,
                      margin: { l: 0, r: 0, t: 0, b: 0 }
                    }}
                    config={{ responsive: true, displayModeBar: false }}
                    style={{ width: '100%' }}
                  />
                </div>
              )}

              {/* Most Used Items */}
              {dashboardData?.topItems && (
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    {dashboardData.topItemsTitle || "Most Used Items This Week"}
                  </h3>
                  <div className="space-y-4">
                    {dashboardData.topItems.map((item, idx) => (
                      <div key={idx}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-700 font-medium">{item.name}</span>
                          <span className="text-gray-600">{item.used}/{item.total}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${item.color || 'bg-teal-600'}`}
                            style={{ width: `${(item.used / item.total) * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;

