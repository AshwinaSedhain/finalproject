// src/components/ThinkingIndicator.jsx
import React, { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';

const steps = [
  "Analyzing prompt...",
  "Generating SQL query...",
  "Querying the database...",
  "Compiling insights...",
];

const ThinkingIndicator = () => {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => (prev + 1) % steps.length);
    }, 1500); // Change step every 1.5 seconds

    return () => clearInterval(stepInterval);
  }, []);

  return (
    <div className="flex gap-3 justify-start">
      <div className="max-w-2xl px-4 py-3 rounded-lg bg-gray-100 text-gray-600 flex items-center">
        <Loader2 className="w-4 h-4 mr-3 animate-spin text-teal-600" />
        <p className="text-sm">{steps[currentStep]}</p>
      </div>
    </div>
  );
};

export default ThinkingIndicator;