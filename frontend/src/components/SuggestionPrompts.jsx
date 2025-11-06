import React from 'react';
import { Lightbulb, TrendingUp, BarChart3, Database, DollarSign, Users, ShoppingCart, Calendar } from 'lucide-react';

const SuggestionPrompts = ({ onSelectPrompt, disabled = false }) => {
  const suggestions = [
    {
      icon: <BarChart3 className="w-4 h-4" />,
      text: "Show me monthly revenue trends",
      category: "Revenue"
    },
    {
      icon: <ShoppingCart className="w-4 h-4" />,
      text: "What are my top 10 best-selling products?",
      category: "Sales"
    },
    {
      icon: <Users className="w-4 h-4" />,
      text: "How many customers do we have?",
      category: "Customers"
    },
    {
      icon: <TrendingUp className="w-4 h-4" />,
      text: "Show me sales performance by region",
      category: "Analytics"
    },
    {
      icon: <Calendar className="w-4 h-4" />,
      text: "What were last month's transactions?",
      category: "Transactions"
    },
    {
      icon: <Database className="w-4 h-4" />,
      text: "Analyze inventory levels",
      category: "Inventory"
    },
    {
      icon: <DollarSign className="w-4 h-4" />,
      text: "Calculate total profit this year",
      category: "Finance"
    },
    {
      icon: <Lightbulb className="w-4 h-4" />,
      text: "How can we improve sales?",
      category: "Insights"
    }
  ];

  const handleClick = (prompt) => {
    if (!disabled) {
      onSelectPrompt(prompt);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-6">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-teal-50 rounded-full mb-3">
          <Lightbulb className="w-5 h-5 text-teal-600" />
          <span className="text-sm font-medium text-teal-700">Try asking:</span>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Get Started with Your Data</h3>
        <p className="text-sm text-gray-600">Click on any suggestion below to explore your database</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
                onClick={(e) => {
                  if (disabled) {
                    e.preventDefault();
                    return;
                  }
                  handleClick(suggestion.text);
                }}
                disabled={disabled}
                className={`
                  group relative p-4 text-left bg-white border-2 border-gray-200 rounded-xl
                  transition-all duration-200
                  ${disabled ? 'opacity-50 cursor-not-allowed pointer-events-none' : 'hover:border-teal-300 hover:shadow-md hover:bg-teal-50 cursor-pointer'}
                `}
          >
            <div className="flex items-start gap-3">
              <div className={`
                p-2 rounded-lg flex-shrink-0 transition-colors
                ${disabled ? 'bg-gray-100 text-gray-400' : 'bg-teal-50 text-teal-600 group-hover:bg-teal-100'}
              `}>
                {suggestion.icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium text-teal-600 uppercase tracking-wide">
                    {suggestion.category}
                  </span>
                </div>
                <p className="text-sm font-medium text-gray-900 group-hover:text-teal-700 transition-colors">
                  {suggestion.text}
                </p>
              </div>
              <div className={`
                opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0
                ${disabled ? 'hidden' : ''}
              `}>
                <svg className="w-5 h-5 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </button>
        ))}
      </div>
      
      <div className="mt-6 text-center">
        <p className="text-xs text-gray-500">
          💡 Tip: You can ask questions in plain English. The AI will understand and generate the right queries for you.
        </p>
      </div>
    </div>
  );
};

export default SuggestionPrompts;

