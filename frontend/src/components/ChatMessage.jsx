// src/components/ChatMessage.jsx
import React, { useState } from 'react';
import { Bot, User, Edit2, Check, X } from 'lucide-react';
import { useTypewriter } from '../hooks/useTypewriter';
import ReactMarkdown from 'react-markdown';

// A new, simple component for the "typing" animation
const TypingIndicator = () => (
  <div className="flex items-center space-x-1 p-2">
    <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce-sm"></span>
    <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce-sm animation-delay-200"></span>
    <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce-sm animation-delay-400"></span>
  </div>
);

const ChatMessage = ({ message, isLoading, onEdit, messageIndex, isLastUserMessage }) => {
  // Safety check
  if (!message || !message.role) {
    return null;
  }

  const isUser = message.role === 'user';
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(message.content || '');
  
  // Apply the typewriter effect only to non-loading assistant messages
  const messageContent = message.content || '';
  const animatedText = !isUser && !isLoading && messageContent ? useTypewriter(messageContent) : messageContent;

  const Avatar = () => (
    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? 'bg-teal-600' : 'bg-gray-700'}`}>
      {isUser ? <User size={18} className="text-white" /> : <Bot size={18} className="text-white" />}
    </div>
  );

  const handleSaveEdit = () => {
    if (editedContent.trim() && onEdit) {
      onEdit(messageIndex, editedContent);
      setIsEditing(false);
    }
  };

  const handleCancelEdit = () => {
    setEditedContent(message.content);
    setIsEditing(false);
  };

  if (isUser && isEditing) {
    return (
      <div className="flex gap-3 my-4 animate-fade-in justify-end">
        <div className="max-w-2xl w-full">
          <div className="bg-white border-2 border-teal-500 rounded-xl shadow-lg p-4">
            <textarea
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none min-h-[80px]"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                  handleSaveEdit();
                } else if (e.key === 'Escape') {
                  handleCancelEdit();
                }
              }}
            />
            <div className="flex items-center gap-2 mt-3 justify-end">
              <button
                onClick={handleCancelEdit}
                className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors flex items-center gap-1"
              >
                <X size={14} />
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                disabled={!editedContent.trim()}
                className="px-3 py-1.5 text-sm bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
              >
                <Check size={14} />
                Save & resend
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">Press Ctrl+Enter to save, Esc to cancel</p>
          </div>
        </div>
        <Avatar />
      </div>
    );
  }

  return (
    <div className={`group flex gap-3 my-4 animate-fade-in ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && <Avatar />}
      <div className={`
        max-w-2xl px-4 py-3 rounded-xl shadow-sm relative
        ${isUser ? 'bg-teal-600 text-white' : 'bg-white text-gray-800 border border-gray-200'}
      `}>
        {isUser && isLastUserMessage && !isLoading && onEdit && (
          <button
            onClick={() => setIsEditing(true)}
            className="absolute -top-2 -left-2 p-1.5 bg-white text-gray-600 rounded-full shadow-md hover:bg-gray-50 opacity-0 group-hover:opacity-100 transition-opacity border border-gray-200"
            title="Edit message"
          >
            <Edit2 size={14} />
          </button>
        )}
        {isLoading ? (
          <TypingIndicator />
        ) : (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{animatedText}</ReactMarkdown>
          </div>
        )}
      </div>
      {isUser && <Avatar />}
    </div>
  );
};

export default ChatMessage;