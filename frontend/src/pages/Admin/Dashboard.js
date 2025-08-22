import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

const AdminDashboard = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Admin Dashboard
        </h1>
        <p className="text-gray-600 mt-1">
          Welcome, {user?.first_name}! System overview and management.
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900">Total Users</h2>
          <p className="text-3xl font-bold text-blue-600 mt-2">1,250</p>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900">Active Students</h2>
          <p className="text-3xl font-bold text-green-600 mt-2">1,125</p>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900">Teachers</h2>
          <p className="text-3xl font-bold text-purple-600 mt-2">85</p>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900">System Health</h2>
          <p className="text-3xl font-bold text-green-600 mt-2">99%</p>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
