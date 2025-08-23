import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { analyticsAPI } from '../../services/api';
import toast from 'react-hot-toast';

const AnalystPredictions = () => {
  const { user } = useAuth();
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPredictions();
  }, [user]);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      const institutionAnalytics = await analyticsAPI.getInstitutionAnalytics();
      setPredictions(institutionAnalytics);
    } catch (err) {
      toast.error('Failed to load predictions');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading predictions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">🔮 Advanced Predictions</h1>
        <p className="text-purple-100 text-lg">Institution-wide predictive analytics and forecasting</p>
      </div>
      
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Prediction Models</h2>
        <p className="text-gray-600">Advanced prediction models and forecasting tools will be displayed here.</p>
      </div>
    </div>
  );
};

export default AnalystPredictions;
