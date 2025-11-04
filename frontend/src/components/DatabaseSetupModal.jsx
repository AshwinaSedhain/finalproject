// File: frontend/src/components/DatabaseSetupModal.jsx

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { testDatabaseConnection } from '../api';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';

const DatabaseSetupModal = ({ isOpen, onSave }) => {
  const [connectionString, setConnectionString] = useState('');
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState(null); // Will hold { status: 'success' | 'error', message: string }
  const { token } = useAuth();

  const handleTestConnection = async () => {
    if (!connectionString) {
      setTestResult({ status: 'error', message: 'Connection string cannot be empty.' });
      return;
    }
    setIsTesting(true);
    setTestResult(null);
    try {
      // ✅ THE FIX IS HERE:
      // We wrap the connection string in a JSON object before sending.
      // This sends the correct format: { "connectionString": "..." } to the backend.
      const result = await testDatabaseConnection({ connectionString: connectionString }, token);
      setTestResult(result);

    } catch (error) {
      // The API function will throw an error on network failure or non-200 responses.
      setTestResult({ status: 'error', message: error.message || 'An unknown error occurred.' });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = () => {
    if (testResult?.status !== 'success') {
      alert("Please ensure the connection is tested successfully before saving.");
      return;
    }
    // The parent component expects an object with the connection string
    onSave({ connectionString });
  };

  // If the parent component decides not to show the modal, we render nothing.
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg p-6 m-4">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Database Configuration</h2>
        <p className="text-gray-600 mb-6">
          To get started, please provide the connection string for the database you want to analyze. The chat functionality will be enabled after a successful connection.
        </p>

        <label htmlFor="db-connection-string" className="block text-sm font-medium text-gray-700 mb-1">Database Connection String</label>
        <textarea
          id="db-connection-string"
          rows={4}
          value={connectionString}
          onChange={(e) => {
            setConnectionString(e.target.value);
            setTestResult(null); // Clear previous test result when user types
          }}
          placeholder="postgresql://user:password@host:port/dbname"
          className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
        />
        <p className="text-xs text-gray-500 mt-1">Example: postgresql://postgres:your_password@db.example.com:5432/postgres</p>
        
        {testResult && (
          <div className={`mt-4 p-3 rounded-md text-sm flex items-center gap-2 ${testResult.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {testResult.status === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
            <span>{testResult.message}</span>
          </div>
        )}

        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={handleTestConnection}
            disabled={isTesting || !connectionString}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium hover:bg-gray-50 disabled:opacity-50 flex items-center justify-center min-w-[140px]"
          >
            {isTesting ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Test Connection'}
          </button>
          <button
            onClick={handleSave}
            disabled={isTesting || testResult?.status !== 'success'}
            className="px-4 py-2 bg-teal-600 text-white rounded-md text-sm font-medium hover:bg-teal-700 disabled:bg-gray-400"
          >
            Save & Continue
          </button>
        </div>
      </div>
    </div>
  );
};

export default DatabaseSetupModal;