// File: frontend/src/api.js

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

export const sendChatMessage = async (prompt, token, signal, connectionString = null) => {
  try {
    const body = { user_prompt: prompt };
    if (connectionString) {
      body.connection_string = connectionString;
    }
    const response = await fetch(`${API_URL}/api/chat/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(body),
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
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_URL}/api/db/test-connection`, {
      method: 'POST',
      headers,
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

export const getDatabaseSummary = async (token) => {
  try {
    const response = await fetch(`${API_URL}/api/chat/database-summary`, {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Failed to get database summary.');
    }
    return response.json();
  } catch (error) {
    console.error('Error fetching database summary:', error);
    throw error;
  }
};

export const getDashboardData = async (token, connectionString = null) => {
  try {
    const url = new URL(`${API_URL}/api/dashboard/data`);
    if (connectionString) {
      url.searchParams.append('connection_string', connectionString);
    }
    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Failed to get dashboard data.');
    }
    return response.json();
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    throw error;
  }
};

export const clearOldDatabaseConnection = async (token, oldConnectionString = null) => {
  try {
    const url = new URL(`${API_URL}/api/database/clear-old`);
    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` 
      },
      body: JSON.stringify({ old_connection_string: oldConnectionString }),
    });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Failed to clear old connection.');
    }
    return response.json();
  } catch (error) {
    console.error('Error clearing old connection:', error);
    // Don't throw - this is a cleanup operation, shouldn't block the user
    return { success: false, error: error.message };
  }
};