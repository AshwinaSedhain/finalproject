// File: frontend/src/api.js

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

export const sendChatMessage = async (prompt, token, signal) => {
  try {
    const response = await fetch(`${API_URL}/api/chat/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ user_prompt: prompt }),
      signal: signal,
    });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.details || data.error || 'Failed to get response.');
    }
    return response.json();
  } catch (error) {
    if (error.name === 'AbortError') {
      return { cancelled: true };
    }
    throw error;
  }
};

export const testDatabaseConnection = async (dbConfig, token) => {
  try {
    const response = await fetch(`${API_URL}/api/db/test-connection`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(dbConfig)
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.message || 'Failed to test connection.');
    }
    return data;
  } catch (error) {
    console.error('Error testing database connection:', error);
    throw new Error(error.message || 'Network error. Is the backend running?');
  }
};

// You can add other functions like getDatabaseSummary here if needed.