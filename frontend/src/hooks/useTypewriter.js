// src/hooks/useTypewriter.js
import { useState, useEffect, useRef } from 'react';

export const useTypewriter = (text, speed = 30, shouldStop = false) => {
  const [displayText, setDisplayText] = useState('');
  const intervalRef = useRef(null);
  const indexRef = useRef(0);

  useEffect(() => {
    // Reset when text changes
    setDisplayText('');
    indexRef.current = 0;
    
    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    // If stopped, show full text immediately
    if (shouldStop && text) {
      setDisplayText(text);
      return;
    }

    // Start typing animation
    if (text && !shouldStop) {
      intervalRef.current = setInterval(() => {
        if (indexRef.current < text.length && !shouldStop) {
          setDisplayText(prev => {
            const newText = text.substring(0, indexRef.current + 1);
            indexRef.current++;
            return newText;
          });
        } else {
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
        }
      }, speed);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [text, speed, shouldStop]);

  // Handle stop signal
  useEffect(() => {
    if (shouldStop && intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
      // Show full text immediately when stopped
      if (text) {
        setDisplayText(text);
      }
    }
  }, [shouldStop, text]);

  return displayText;
};