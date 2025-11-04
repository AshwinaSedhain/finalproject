// File: frontend/src/api.js

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

export const sendChatMessage = async (prompt, token) => {
  try {
    const response = await fetch(`${API_URL}/api/chat/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ user_prompt: prompt })
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.details || data.error || 'Failed to get response from server.');
    }
    return data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};

export const getDatabaseSummary = async (token) => {
  try {
    const response = await fetch(`${API_URL}/api/chat/database-summary`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.details || 'Failed to fetch database summary.');
    }
    return data;
  } catch (error) {
    console.error('Error fetching database summary:', error);
    throw error;
  }
};

export const testDatabaseConnection = async (dbConfig, token) => {
  try {
    const response = await fetch(`${API_URL}/api/db/test-connection`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(dbConfig)
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.details || 'Failed to test database connection.');
    }
    return data;
  } catch (error) {
    console.error('Error testing database connection:', error);
    throw error;
  }
};