import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

const AnalystDashboard = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Analyst Dashboard
        </h1>
        <p className="text-gray-600 mt-1">
          Welcome, {user?.first_name}! Advanced analytics and insights.
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900">ML Model Accuracy</h2>
          <p className="text-3xl font-bold text-green-600 mt-2">87.2%</p>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900">Predictions Made</h2>
          <p className="text-3xl font-bold text-blue-600 mt-2">2,450</p>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900">Data Points</h2>
          <p className="text-3xl font-bold text-purple-600 mt-2">1.2M</p>
        </div>
      </div>
    </div>
  );
};

export default AnalystDashboard;
