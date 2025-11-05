// File: frontend/src/components/DatabaseSetupModal.jsx

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { testDatabaseConnection } from '../api';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';

const DatabaseSetupModal = ({ isOpen, onSave }) => {
  const [connectionString, setConnectionString] = useState('');
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const { token } = useAuth();

  const handleTestConnection = async () => {
    if (!connectionString) {
      setTestResult({ status: 'error', message: 'Connection string cannot be empty.' });
      return;
    }
    setIsTesting(true);
    setTestResult(null);
    try {
      const result = await testDatabaseConnection({ connectionString: connectionString }, token);
      setTestResult(result);
    } catch (error) {
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
    setIsSaving(true);
    setTimeout(() => {
      onSave({ connectionString });
    }, 3000);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg p-6 m-4">
        {isSaving ? (
          <div className="text-center p-8">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4 animate-pulse" />
            <h2 className="text-xl font-semibold text-gray-800">Connection Saved!</h2>
            <p className="text-gray-600 mt-2">Redirecting you to the dashboard...</p>
          </div>
        ) : (
          <>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Database Configuration</h2>
            <p className="text-gray-600 mb-6">To get started, please connect to the database you wish to analyze.</p>
            <label htmlFor="db-connection-string" className="block text-sm font-medium text-gray-700 mb-1">Database Connection String</label>
            <textarea
              id="db-connection-string"
              rows={4}
              value={connectionString}
              onChange={(e) => {
                setConnectionString(e.target.value);
                setTestResult(null);
              }}
              placeholder="postgresql://user:password@host:port/dbname"
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            />
            {testResult && (
              <div className={`mt-4 p-3 rounded-md text-sm flex items-center gap-2 ${testResult.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {testResult.status === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
                <span>{testResult.message}</span>
              </div>
            )}
            <div className="mt-6 flex justify-end gap-3">
              <button onClick={handleTestConnection} disabled={isTesting || !connectionString} className="px-4 py-2 border rounded-md text-sm font-medium hover:bg-gray-50 disabled:opacity-50">
                {isTesting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Test Connection'}
              </button>
              <button onClick={handleSave} disabled={isTesting || testResult?.status !== 'success'} className="px-4 py-2 bg-teal-600 text-white rounded-md text-sm font-medium hover:bg-teal-700 disabled:bg-gray-400">
                Save & Continue
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default DatabaseSetupModal;