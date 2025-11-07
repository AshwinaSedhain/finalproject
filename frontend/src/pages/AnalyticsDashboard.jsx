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
  }, [dbConfig?.connectionString]); // Re-fetch when connection string changes

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
          <RefreshCw className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-900 font-semibold mb-2">Error loading dashboard</p>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
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
      <div className="w-16 bg-white border-r border-gray-200 flex flex-col items-center py-6 gap-4">
        <button 
          className="p-3 rounded-lg bg-blue-50 hover:bg-blue-100 transition-colors border-2 border-blue-200"
          title="Analytics Dashboard"
        >
          <Database className="w-6 h-6 text-blue-600" />
        </button>
        <button 
          onClick={() => navigate('/chat')}
          className="p-3 rounded-lg hover:bg-gray-100 transition-colors border-2 border-transparent"
          title="Chat with Database"
        >
          <BarChart3 className="w-6 h-6 text-gray-600" />
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
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Refresh"
              >
                <RefreshCw className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          </div>

          {/* Chat with Database Button - Prominent */}
          <div className="mb-6 bg-white rounded-xl p-6 border border-gray-200 shadow-md">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Ready to Explore Your Data?</h3>
                <p className="text-gray-600">Ask questions in natural language and get instant insights from your database.</p>
              </div>
              <button
                onClick={() => navigate('/chat')}
                className="px-8 py-4 bg-teal-500 text-white rounded-lg hover:bg-teal-600 transition-all font-semibold text-lg shadow-md hover:shadow-lg flex items-center gap-3 whitespace-nowrap"
              >
                <BarChart3 className="w-6 h-6" />
                Chat with Database
                <span className="text-white">→</span>
              </button>
            </div>
          </div>

          {/* Analytics Overview Cards - 6 KPIs */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Analytics Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
              {dashboardData?.metrics?.map((metric, index) => (
                <div
                  key={index}
                  className="bg-white rounded-xl p-6 shadow-md border border-gray-200 relative overflow-hidden hover:border-gray-300 hover:shadow-lg transition-all"
                >
                  <div className="relative">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="p-2 rounded-lg bg-gray-50 border border-gray-200">
                        <span className="text-lg">{metric.icon || '📊'}</span>
                      </div>
                      <span className="text-sm font-medium text-gray-700">{metric.label}</span>
                    </div>
                    <div className="text-3xl font-bold text-gray-900">{metric.value}</div>
                    {metric.unit && <span className="text-sm text-gray-600 ml-2">{metric.unit}</span>}
                    {/* Small colorful line chart area at bottom */}
                    <div className="mt-4 h-12 relative">
                      <svg className="w-full h-full" viewBox="0 0 100 40" preserveAspectRatio="none">
                        <defs>
                          <linearGradient id={`gradient-${index}`} x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stopColor={['#14b8a6', '#f97316', '#3b82f6', '#8b5cf6', '#ec4899', '#10b981'][index % 6]} stopOpacity="0.3" />
                            <stop offset="100%" stopColor={['#14b8a6', '#f97316', '#3b82f6', '#8b5cf6', '#ec4899', '#10b981'][index % 6]} stopOpacity="0" />
                          </linearGradient>
                        </defs>
                        <path
                          d={`M 0,${40 - Math.random() * 10} L 20,${40 - Math.random() * 15} L 40,${40 - Math.random() * 20} L 60,${40 - Math.random() * 12} L 80,${40 - Math.random() * 18} L 100,${40 - Math.random() * 8}`}
                          fill={`url(#gradient-${index})`}
                          stroke={['#14b8a6', '#f97316', '#3b82f6', '#8b5cf6', '#ec4899', '#10b981'][index % 6]}
                          strokeWidth="2"
                        />
                      </svg>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Charts Grid - Row 1: Three Horizontal Bar Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* Sales by Item */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-md">
              <div className="p-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Sales by Item</h3>
              </div>
              <div className="p-4" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                {dashboardData?.topSellingChart ? (
                  <Plot
                    data={dashboardData.topSellingChart.data}
                    layout={{
                      ...dashboardData.topSellingChart.layout,
                      height: 350,
                      margin: { l: 200, r: 20, t: 20, b: 40 }
                    }}
                    config={{ responsive: true, displayModeBar: false }}
                    style={{ width: '100%' }}
                  />
                ) : (
                  <div className="flex items-center justify-center h-80 text-gray-500 text-sm">
                    No data available
                  </div>
                )}
              </div>
            </div>

            {/* Sales by Item Category */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-md">
              <div className="p-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Sales by Item Category</h3>
              </div>
              <div className="p-4">
                {dashboardData?.salesByCategoryChart ? (
                  <Plot
                    data={dashboardData.salesByCategoryChart.data}
                    layout={{
                      ...dashboardData.salesByCategoryChart.layout,
                      height: 350,
                      margin: { l: 150, r: 20, t: 20, b: 40 }
                    }}
                    config={{ responsive: true, displayModeBar: false }}
                    style={{ width: '100%' }}
                  />
                ) : (
                  <div className="flex items-center justify-center h-80 text-slate-600 text-sm">
                    No data available
                  </div>
                )}
              </div>
            </div>

            {/* Sales by Product Group */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-md">
              <div className="p-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Sales by Product Group</h3>
              </div>
              <div className="p-4" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                {dashboardData?.salesByGroupChart ? (
                  <Plot
                    data={dashboardData.salesByGroupChart.data}
                    layout={{
                      ...dashboardData.salesByGroupChart.layout,
                      height: 350,
                      margin: { l: 150, r: 20, t: 20, b: 40 }
                    }}
                    config={{ responsive: true, displayModeBar: false }}
                    style={{ width: '100%' }}
                  />
                ) : (
                  <div className="flex items-center justify-center h-80 text-slate-600 text-sm">
                    No data available
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Charts Grid - Row 2: Pie Chart and Unsold Items */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Sales by Division Pie Chart */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Sales by Division</h3>
              {dashboardData?.salesByDivisionChart ? (
                <Plot
                  data={dashboardData.salesByDivisionChart.data}
                  layout={{
                    ...dashboardData.salesByDivisionChart.layout,
                    height: 300
                  }}
                  config={{ responsive: true, displayModeBar: false }}
                  style={{ width: '100%' }}
                />
              ) : (
                <div className="flex items-center justify-center h-80 text-slate-600 text-sm">
                  No data available
                </div>
              )}
            </div>

            {/* Unsold Items List */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Unsold Items
              </h3>
              {dashboardData?.unsoldItems && dashboardData.unsoldItems.length > 0 ? (
                <div>
                  <p className="text-sm text-gray-600 mb-4">
                    {dashboardData.unsoldItems.length} out of {dashboardData.unsoldItems.length + 10} items are unsold
                  </p>
                  <div className="space-y-2 max-h-80 overflow-y-auto">
                    {dashboardData.unsoldItems.map((item, idx) => {
                      const itemColors = [
                        'bg-orange-50 border-orange-200',
                        'bg-green-50 border-green-200',
                        'bg-blue-50 border-blue-200',
                        'bg-purple-50 border-purple-200',
                        'bg-teal-50 border-teal-200',
                        'bg-pink-50 border-pink-200'
                      ];
                      const itemColor = itemColors[idx % itemColors.length];
                      return (
                        <div key={idx} className={`p-3 ${itemColor} rounded-lg border`}>
                          <span className="text-sm font-medium text-gray-900">
                            {item.id && item.id !== 'None' ? `${item.id} - ` : ''}{item.name}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-80 text-gray-500 text-sm">
                  No unsold items found
                </div>
              )}
            </div>
          </div>

          {/* Revenue Overview Pie Chart (if available) */}
          {dashboardData?.pieChart && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-md p-6 mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Financial Overview</h3>
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
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;

