import React from 'react';
import { LogOut, Menu, User, Settings, BarChart3, Database, LayoutDashboard } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

const Navbar = ({ onMenuToggle, onSettingsClick, hasOverview, activeView, onOverviewClick, onChatClick }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const handleLogout = async () => {
    await logout();
    navigate('/');
  };
  
  const isDashboard = location.pathname === '/dashboard'; // Analytics Dashboard
  const isChat = location.pathname === '/chat'; // Chat Interface

  return (
    <nav className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center gap-3">
        {onMenuToggle && (
          <button onClick={onMenuToggle} className="p-2 hover:bg-gray-100 rounded-lg">
            <Menu className="w-5 h-5" />
          </button>
        )}

        <button 
          onClick={() => navigate('/')}
          className="flex items-center gap-2 hover:opacity-80 transition-opacity cursor-pointer"
        >
          <div className="relative">
            <BarChart3 className="w-6 h-6 text-teal-600" />
          </div>
          <span className="font-semibold text-lg text-gray-900">
            InsightAI
          </span>
        </button>
      </div>
      
      <div className="flex items-center gap-3">
        {/* Navigation between Dashboard (Analytics) and Chat */}
        {isDashboard && (
          <button
            onClick={() => navigate('/chat')}
            className="flex items-center gap-2 px-3 py-2 rounded-lg transition-colors hover:bg-teal-50 text-teal-700"
            title="Chat with Database"
          >
            <BarChart3 className="w-4 h-4" />
            <span className="text-sm font-medium hidden sm:inline">Chat with Database</span>
          </button>
        )}
        
        {isChat && (
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 px-3 py-2 rounded-lg transition-colors hover:bg-teal-50 text-teal-700"
            title="View Analytics Dashboard"
          >
            <LayoutDashboard className="w-4 h-4" />
            <span className="text-sm font-medium hidden sm:inline">Dashboard</span>
          </button>
        )}
        
{hasOverview && activeView==="chat" &&(
  <button
    onClick={() => onOverviewClick()}
    className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors
      ${activeView === "overview" ? "bg-teal-50 text-teal-700" : "hover:bg-teal-50 text-teal-700"}
    `}
    title="View Database Overview"
  >
    <Database className="w-4 h-4" />
    <span className="text-sm font-medium hidden sm:inline">Overview</span>
  </button>
)}

{ activeView==="overview" &&(
        <button
  onClick={() => onChatClick()}
  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors
    ${activeView === "chat" ? "bg-teal-50 text-teal-700" : "hover:bg-teal-50 text-teal-700"}
  `}
  title="Chat"
>
  <BarChart3 className="w-4 h-4" />
  <span className="text-sm font-medium hidden sm:inline">Chat</span>
</button>

  )}

        {onSettingsClick && (
          <button
            onClick={onSettingsClick}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Database Settings"
          >
            <Settings className="w-5 h-5 text-gray-600" />
          </button>
        )}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg">
          <User className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium">{user?.name || user?.email}</span>
        </div>
        <button
          onClick={handleLogout}
          className="p-2 hover:bg-red-50 text-red-600 rounded-lg transition-colors"
          title="Logout"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
