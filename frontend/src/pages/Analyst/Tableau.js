import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

const AnalystTableau = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">📊 Tableau Integration</h1>
        <p className="text-purple-100 text-lg">Advanced data visualization with Tableau</p>
      </div>
      
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Tableau Dashboards</h2>
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Tableau Integration</h3>
          <p className="text-gray-500 mb-4">Connect to Tableau for advanced data visualization</p>
          <button className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg font-medium transition-colors">
            Open Tableau
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnalystTableau;
