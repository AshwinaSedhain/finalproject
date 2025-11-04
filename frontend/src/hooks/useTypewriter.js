// src/hooks/useTypewriter.js
import { useState, useEffect } from 'react';

export const useTypewriter = (text, speed = 30) => {
  const [displayText, setDisplayText] = useState('');

  useEffect(() => {
    let i = 0;
    if (text) {
      const typingInterval = setInterval(() => {
        if (i < text.length) {
          setDisplayText(prev => prev + text.charAt(i));
          i++;
        } else {
          clearInterval(typingInterval);
        }
      }, speed);

      return () => {
        clearInterval(typingInterval);
      };
    }
  }, [text, speed]);

  return displayText;
};