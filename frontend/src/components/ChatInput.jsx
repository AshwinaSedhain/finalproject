// File: frontend/src/components/ChatInput.jsx

import React, { useState } from 'react';
import { Send, Square } from 'lucide-react';

// ChatGPT-style chat input: Send button becomes Stop button during generation
const ChatInput = ({ onSend, disabled, isLoading, onStop, suggestions = [] }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    // STRICT: Block if loading or disabled
    if (isLoading || disabled || !message.trim()) {
      if (e) e.preventDefault();
      return;
    }
    onSend(message);
    setMessage('');
  };

  const handleKeyPress = (e) => {
    // STRICT: Block Enter key if loading
    if (e.key === 'Enter' && !e.shiftKey) {
      if (isLoading) {
        e.preventDefault();
        return;
      }
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Handle stop button click - always enabled during loading
  const handleStopClick = (e) => {
    if (e) e.preventDefault();
    if (isLoading && onStop) {
      onStop();
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white">
      {/* Quick Suggestions - Hidden when loading */}
      {suggestions.length > 0 && !isLoading && (
        <div className="px-4 pt-3 pb-2 border-b border-gray-100">
          <div className="flex flex-wrap gap-2">
            {suggestions.slice(0, 4).map((suggestion, index) => (
              <button
                key={index}
                onClick={(e) => {
                  if (isLoading || disabled) {
                    e.preventDefault();
                    return;
                  }
                  onSend(suggestion);
                }}
                disabled={disabled || isLoading}
                className="px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-50 border border-gray-200 rounded-full hover:bg-teal-50 hover:border-teal-300 hover:text-teal-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
      
      <div className="p-4">
        <div className="relative">
          <textarea
            rows={1}
            value={message}
            onChange={(e) => {
              // STRICT: Block typing if loading
              if (isLoading) {
                e.preventDefault();
                return;
              }
              setMessage(e.target.value);
            }}
            onKeyDown={(e) => {
              // Block all input during loading
              if (isLoading) {
                e.preventDefault();
                return;
              }
              handleKeyPress(e);
            }}
            placeholder={isLoading ? "Generating response..." : "Ask for reports or insights..."}
            className={`w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none transition-colors ${
              isLoading 
                ? 'bg-gray-100 cursor-not-allowed opacity-60 pointer-events-none' 
                : 'bg-white'
            } disabled:bg-gray-100 disabled:cursor-not-allowed`}
            disabled={disabled || isLoading}
            readOnly={isLoading}
          />
          
          {/* ChatGPT-style: Send button becomes Stop button during generation */}
          <button
            onClick={isLoading ? handleStopClick : handleSubmit}
            disabled={disabled || (!isLoading && !message.trim())}
            className={`absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-full transition-all ${
              isLoading
                ? 'bg-gray-700 hover:bg-gray-800 text-white cursor-pointer shadow-lg'
                : 'bg-teal-600 hover:bg-teal-700 text-white disabled:bg-gray-300 disabled:cursor-not-allowed'
            }`}
            title={isLoading ? "Stop generating" : "Send message"}
            type="button"
          >
            {isLoading ? (
              <Square size={18} className="fill-current" />
            ) : (
              <Send size={18} />
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;