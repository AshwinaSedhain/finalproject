// src/components/ChatMessage.jsx
import React from 'react';
import { Bot, User } from 'lucide-react';
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

const ChatMessage = ({ message, isLoading }) => {
  const isUser = message.role === 'user';
  
  // Apply the typewriter effect only to non-loading assistant messages
  const animatedText = !isUser && !isLoading ? useTypewriter(message.content) : message.content;

  const Avatar = () => (
    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? 'bg-teal-600' : 'bg-gray-700'}`}>
      {isUser ? <User size={18} className="text-white" /> : <Bot size={18} className="text-white" />}
    </div>
  );

  return (
    <div className={`flex gap-3 my-4 animate-fade-in ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && <Avatar />}
      <div className={`
        max-w-2xl px-4 py-3 rounded-xl shadow-sm
        ${isUser ? 'bg-teal-600 text-white' : 'bg-white text-gray-800 border border-gray-200'}
      `}>
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