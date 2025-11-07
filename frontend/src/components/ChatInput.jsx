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
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    console.log('[ChatInput] Stop button clicked, isLoading:', isLoading, 'onStop:', !!onStop);
    if (isLoading && onStop) {
      console.log('[ChatInput] Calling onStop handler...');
      onStop();
    } else {
      console.warn('[ChatInput] Stop button clicked but isLoading is', isLoading, 'or onStop is', !!onStop);
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
                className="px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-50 border border-gray-200 rounded-full hover:bg-gray-100 hover:border-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
      
      <div className="p-4 max-w-4xl mx-auto">
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
            placeholder={isLoading ? "Generating response..." : "Message InsightAI..."}
            className={`w-full px-4 py-3 pr-14 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-[#0b93f6] resize-none transition-colors text-sm ${
              isLoading 
                ? 'bg-gray-100 cursor-not-allowed opacity-60 pointer-events-none' 
                : 'bg-white'
            } disabled:bg-gray-100 disabled:cursor-not-allowed`}
            disabled={disabled || isLoading}
            readOnly={isLoading}
            style={{ maxHeight: '200px', minHeight: '44px' }}
          />
          
          {/* ChatGPT-style: Send button becomes Stop button during generation - ALWAYS VISIBLE WHEN LOADING */}
          {isLoading ? (
            <button
              onClick={handleStopClick}
              className="absolute right-2 bottom-2 p-2 rounded-lg bg-gray-700 hover:bg-gray-800 text-white cursor-pointer shadow-md transition-all flex items-center justify-center"
              title="Stop generating"
              type="button"
            >
              <Square size={16} className="fill-current" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={disabled || !message.trim()}
              className="absolute right-2 bottom-2 p-2 rounded-lg bg-[#0b93f6] hover:bg-[#0a7bc8] text-white disabled:bg-gray-300 disabled:cursor-not-allowed transition-all flex items-center justify-center"
              title="Send message"
              type="button"
            >
              <Send size={16} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatInput;