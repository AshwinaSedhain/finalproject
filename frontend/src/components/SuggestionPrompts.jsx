import React, { useState, useEffect } from 'react';
import { Lightbulb, TrendingUp, BarChart3, Database, DollarSign, Users, ShoppingCart, Calendar, Package, Target, PieChart, MapPin, Clock, AlertCircle, CheckCircle, XCircle, Activity, Zap } from 'lucide-react';

const SuggestionPrompts = ({ onSelectPrompt, disabled = false }) => {
  // Large pool of suggestions - will rotate dynamically
  const allSuggestions = [
    // Revenue & Sales
    { icon: <BarChart3 className="w-4 h-4" />, text: "Show me monthly revenue trends", category: "Revenue" },
    { icon: <TrendingUp className="w-4 h-4" />, text: "What are my top 10 best-selling products?", category: "Sales" },
    { icon: <DollarSign className="w-4 h-4" />, text: "Calculate total profit this year", category: "Finance" },
    { icon: <BarChart3 className="w-4 h-4" />, text: "Show me daily sales for the last 30 days", category: "Sales" },
    { icon: <PieChart className="w-4 h-4" />, text: "Break down revenue by product category", category: "Revenue" },
    { icon: <TrendingUp className="w-4 h-4" />, text: "Compare this month's sales to last month", category: "Analytics" },
    { icon: <DollarSign className="w-4 h-4" />, text: "What is the average order value?", category: "Finance" },
    { icon: <BarChart3 className="w-4 h-4" />, text: "Show me revenue growth over the past year", category: "Revenue" },
    
    // Products & Inventory
    { icon: <ShoppingCart className="w-4 h-4" />, text: "What products are running low in stock?", category: "Inventory" },
    { icon: <Package className="w-4 h-4" />, text: "List all products with zero sales", category: "Products" },
    { icon: <Database className="w-4 h-4" />, text: "Analyze inventory levels by category", category: "Inventory" },
    { icon: <ShoppingCart className="w-4 h-4" />, text: "Which products have the highest profit margin?", category: "Products" },
    { icon: <Package className="w-4 h-4" />, text: "Show me products that haven't sold in 90 days", category: "Inventory" },
    { icon: <Database className="w-4 h-4" />, text: "What are the most popular product categories?", category: "Products" },
    
    // Customers
    { icon: <Users className="w-4 h-4" />, text: "How many customers do we have?", category: "Customers" },
    { icon: <Users className="w-4 h-4" />, text: "Who are our top 10 customers by purchase amount?", category: "Customers" },
    { icon: <Users className="w-4 h-4" />, text: "Show me customer acquisition trends", category: "Customers" },
    { icon: <Users className="w-4 h-4" />, text: "What is the average customer lifetime value?", category: "Customers" },
    
    // Time-based Analysis
    { icon: <Calendar className="w-4 h-4" />, text: "What were last month's transactions?", category: "Transactions" },
    { icon: <Clock className="w-4 h-4" />, text: "Show me sales by day of the week", category: "Analytics" },
    { icon: <Calendar className="w-4 h-4" />, text: "Compare Q1 vs Q2 performance", category: "Analytics" },
    { icon: <Clock className="w-4 h-4" />, text: "What are the busiest hours for sales?", category: "Analytics" },
    
    // Geographic & Location
    { icon: <MapPin className="w-4 h-4" />, text: "Show me sales performance by region", category: "Analytics" },
    { icon: <MapPin className="w-4 h-4" />, text: "Which location has the highest sales?", category: "Analytics" },
    { icon: <MapPin className="w-4 h-4" />, text: "Break down revenue by city", category: "Analytics" },
    
    // Insights & Recommendations
    { icon: <Lightbulb className="w-4 h-4" />, text: "How can we improve sales?", category: "Insights" },
    { icon: <Target className="w-4 h-4" />, text: "What are the best opportunities for growth?", category: "Insights" },
    { icon: <Lightbulb className="w-4 h-4" />, text: "Recommend products to promote", category: "Insights" },
    { icon: <Zap className="w-4 h-4" />, text: "What actions should we take to increase revenue?", category: "Insights" },
    
    // Performance & Metrics
    { icon: <Activity className="w-4 h-4" />, text: "Show me key performance indicators", category: "Analytics" },
    { icon: <CheckCircle className="w-4 h-4" />, text: "What are our most successful products?", category: "Products" },
    { icon: <AlertCircle className="w-4 h-4" />, text: "Which products need attention?", category: "Products" },
    { icon: <Activity className="w-4 h-4" />, text: "Calculate conversion rates", category: "Analytics" },
    
    // Comparisons
    { icon: <BarChart3 className="w-4 h-4" />, text: "Compare this year to last year", category: "Analytics" },
    { icon: <TrendingUp className="w-4 h-4" />, text: "Show me top vs bottom performing products", category: "Analytics" },
    { icon: <PieChart className="w-4 h-4" />, text: "What percentage of revenue comes from each category?", category: "Revenue" },
    
    // Specific Queries
    { icon: <ShoppingCart className="w-4 h-4" />, text: "Find all orders above $1000", category: "Transactions" },
    { icon: <Database className="w-4 h-4" />, text: "Show me items with negative profit", category: "Finance" },
    { icon: <XCircle className="w-4 h-4" />, text: "List all cancelled or returned orders", category: "Transactions" },
    { icon: <Package className="w-4 h-4" />, text: "What products are out of stock?", category: "Inventory" }
  ];

  // State to track which suggestions to show (rotates dynamically)
  const [displayedSuggestions, setDisplayedSuggestions] = useState([]);

  // Function to randomly select 8 suggestions from the pool
  const getRandomSuggestions = () => {
    const shuffled = [...allSuggestions].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, 8);
  };

  // Initialize and rotate suggestions
  useEffect(() => {
    // Set initial suggestions
    setDisplayedSuggestions(getRandomSuggestions());
    
    // Rotate suggestions every 30 seconds
    const rotationInterval = setInterval(() => {
      setDisplayedSuggestions(getRandomSuggestions());
    }, 30000); // 30 seconds

    return () => clearInterval(rotationInterval);
  }, []);

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
        {displayedSuggestions.map((suggestion, index) => (
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

