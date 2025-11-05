// File: frontend/src/components/Sidebar.jsx

import React from "react";
import { X, Plus, MessageSquare, Trash2 } from "lucide-react";

const Sidebar = ({
  isOpen,
  onClose,
  chatHistory,
  onSelectChat,
  activeChatId,
  showCloseButton,
  onNewChat,
  onDeleteChat
}) => {
  return (
    <>
      {/* Overlay for mobile view to close the sidebar when clicking outside */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={onClose}
        ></div>
      )}

      {/* The Sidebar Itself */}
      <div
        className={`fixed top-0 left-0 h-full z-40 w-72 bg-white border-r border-gray-200 flex flex-col transition-transform duration-300
          ${isOpen ? "translate-x-0" : "-translate-x-full"}
          lg:relative lg:translate-x-0
        `}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 flex-shrink-0">
          <h2 className="text-lg font-semibold text-gray-900">Chat History</h2>
          <div className="flex items-center gap-2">
            <button
              onClick={onNewChat}
              className="p-2 hover:bg-gray-100 rounded-lg"
              title="Start New Chat"
            >
              <Plus className="w-5 h-5 text-gray-600" />
            </button>
            {showCloseButton && (
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-lg lg:hidden" // Only show close button on smaller screens
                title="Close Sidebar"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            )}
          </div>
        </div>

        {/* Chat History List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1 mt-2">
          {chatHistory && chatHistory.length > 0 ? (
            chatHistory.map((chat) => (
              // Use a div as a 'group' for hover effects
              <div key={chat.id} className="group relative w-full">
                <button
                  onClick={() => onSelectChat(chat)}
                  className={`w-full text-left px-3 py-2 rounded-lg flex items-center gap-3 transition-colors
                    ${activeChatId === chat.id
                      ? "bg-teal-50 text-teal-800 font-medium"
                      : "hover:bg-gray-100 text-gray-700"
                    }`}
                >
                  <MessageSquare size={16} className="flex-shrink-0" />
                  <span className="truncate flex-1">{chat.title || "New Conversation"}</span>
                </button>
                
                {/* The Delete Button */}
                {/* It appears only on hover of the parent div ('group-hover') */}
                <button
                  onClick={(e) => {
                    e.stopPropagation(); // Prevents selecting the chat when clicking delete
                    if (window.confirm(`Are you sure you want to delete "${chat.title || 'this chat'}"?`)) {
                      onDeleteChat(chat.id);
                    }
                  }}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded-md text-gray-400 hover:bg-red-500/10 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Delete Chat"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-400 text-center mt-4 px-4">
              No conversations yet. Start by asking a question!
            </p>
          )}
        </div>
      </div>
    </>
  );
};

export default Sidebar;