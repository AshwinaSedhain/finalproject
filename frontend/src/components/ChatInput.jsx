// File: frontend/src/components/ChatInput.jsx

import React, { useState } from 'react';
import { Send, Loader2, Square } from 'lucide-react';

// ✅ UPDATED: Now accepts an onStop function
const ChatInput = ({ onSend, disabled, isLoading, onStop }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      onSend(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // ✅ NEW: The "Stop generating" button UI
  if (isLoading) {
    return (
      <div className="p-4 border-t border-gray-200 bg-white flex justify-center">
        <button
          onClick={onStop}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-100 flex items-center gap-2"
        >
          <Square size={16} />
          Stop generating
        </button>
      </div>
    );
  }

  // Original input UI
  return (
    <div className="p-4 border-t border-gray-200 bg-white">
      <div className="relative">
        <textarea
          rows={1}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask for reports or insights..."
          className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
          disabled={disabled}
        />
        <button
          onClick={handleSubmit}
          disabled={disabled || !message.trim()}
          className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-teal-600 text-white rounded-full hover:bg-teal-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
};

export default ChatInput;