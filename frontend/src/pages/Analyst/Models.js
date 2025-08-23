import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { analyticsAPI } from '../../services/api';
import toast from 'react-hot-toast';

const AnalystModels = () => {
  const { user } = useAuth();
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);
  const [trainingData, setTrainingData] = useState(null);
  const [showTrainingModal, setShowTrainingModal] = useState(false);

  useEffect(() => {
    fetchModels();
  }, [user]);

  const fetchModels = async () => {
    try {
      setLoading(true);
      setError(null);

      // Mock model data - in real implementation, this would come from API
      const mockModels = [
        {
          id: 'dropout_prediction',
          name: 'Dropout Prediction Model',
          type: 'Classification',
          algorithm: 'Random Forest',
          accuracy: 0.87,
          precision: 0.84,
          recall: 0.89,
          f1_score: 0.86,
          last_trained: '2024-01-10T10:00:00Z',
          status: 'active',
          description: 'Predicts student dropout risk based on academic performance, attendance, and engagement metrics.',
          features: ['GPA', 'Attendance Rate', 'Assignment Completion', 'Course Engagement', 'Financial Aid Status'],
          training_samples: 15420,
          version: '2.1.0'
        },
        {
          id: 'grade_prediction',
          name: 'Grade Prediction Model',
          type: 'Regression',
          algorithm: 'Gradient Boosting',
          accuracy: 0.82,
          mae: 0.34,
          rmse: 0.45,
          r2_score: 0.78,
          last_trained: '2024-01-08T14:30:00Z',
          status: 'active',
          description: 'Predicts final course grades based on mid-term performance and historical data.',
          features: ['Mid-term Grades', 'Assignment Scores', 'Attendance', 'Previous Course Performance', 'Study Hours'],
          training_samples: 23150,
          version: '1.8.2'
        },
        {
          id: 'engagement_prediction',
          name: 'Student Engagement Model',
          type: 'Classification',
          algorithm: 'Neural Network',
          accuracy: 0.79,
          precision: 0.76,
          recall: 0.81,
          f1_score: 0.78,
          last_trained: '2024-01-05T09:15:00Z',
          status: 'training',
          description: 'Identifies students at risk of low engagement based on learning analytics.',
          features: ['Login Frequency', 'Resource Access', 'Discussion Participation', 'Assignment Timeliness'],
          training_samples: 18750,
          version: '1.2.0'
        },
        {
          id: 'performance_forecasting',
          name: 'Academic Performance Forecasting',
          type: 'Time Series',
          algorithm: 'LSTM',
          accuracy: 0.74,
          mae: 0.28,
          rmse: 0.38,
          mape: 12.5,
          last_trained: '2024-01-12T16:45:00Z',
          status: 'inactive',
          description: 'Forecasts semester-end academic performance trends for institutional planning.',
          features: ['Historical GPA', 'Course Difficulty', 'Class Size', 'Instructor Rating', 'Semester Trends'],
          training_samples: 8920,
          version: '0.9.1'
        }
      ];

      setModels(mockModels);
    } catch (err) {
      console.error('Error fetching models:', err);
      setError('Failed to load ML models. Please try again.');
      toast.error('Failed to load models');
    } finally {
      setLoading(false);
    }
  };

  const handleTrainModel = async (modelId) => {
    try {
      toast.loading('Starting model training...', { id: 'training' });
      
      // Mock training process
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Update model status
      setModels(prev => prev.map(model => 
        model.id === modelId 
          ? { ...model, status: 'training', last_trained: new Date().toISOString() }
          : model
      ));

      toast.success('Model training started successfully', { id: 'training' });
    } catch (err) {
      console.error('Error training model:', err);
      toast.error('Failed to start model training', { id: 'training' });
    }
  };

  const handleDeployModel = async (modelId) => {
    try {
      toast.loading('Deploying model...', { id: 'deploy' });
      
      // Mock deployment process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Update model status
      setModels(prev => prev.map(model => 
        model.id === modelId 
          ? { ...model, status: 'active' }
          : model
      ));

      toast.success('Model deployed successfully', { id: 'deploy' });
    } catch (err) {
      console.error('Error deploying model:', err);
      toast.error('Failed to deploy model', { id: 'deploy' });
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'training': return 'bg-yellow-100 text-yellow-800';
      case 'inactive': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return '✅';
      case 'training': return '🔄';
      case 'inactive': return '⏸️';
      default: return '❓';
    }
  };

  const getAlgorithmColor = (algorithm) => {
    const colors = {
      'Random Forest': 'bg-blue-100 text-blue-800',
      'Gradient Boosting': 'bg-purple-100 text-purple-800',
      'Neural Network': 'bg-pink-100 text-pink-800',
      'LSTM': 'bg-indigo-100 text-indigo-800'
    };
    return colors[algorithm] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading ML models...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">🤖</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Models Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchModels}
            className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Reload Models
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">🤖 ML Model Management</h1>
        <p className="text-purple-100 text-lg">
          Manage, train, and deploy machine learning models for educational analytics
        </p>
      </div>

      {/* Model Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Active Models</p>
              <p className="text-3xl font-bold">{models.filter(m => m.status === 'active').length}</p>
            </div>
            <div className="text-4xl opacity-80">✅</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-500 to-orange-500 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100 text-sm">Training</p>
              <p className="text-3xl font-bold">{models.filter(m => m.status === 'training').length}</p>
            </div>
            <div className="text-4xl opacity-80">🔄</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Avg Accuracy</p>
              <p className="text-3xl font-bold">
                {(models.reduce((sum, m) => sum + (m.accuracy || 0), 0) / models.length * 100).toFixed(1)}%
              </p>
            </div>
            <div className="text-4xl opacity-80">🎯</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Total Samples</p>
              <p className="text-3xl font-bold">
                {(models.reduce((sum, m) => sum + (m.training_samples || 0), 0) / 1000).toFixed(0)}K
              </p>
            </div>
            <div className="text-4xl opacity-80">📊</div>
          </div>
        </div>
      </div>

      {/* Models Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {models.map((model) => (
          <div key={model.id} className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-800">{model.name}</h3>
                <p className="text-gray-600 text-sm mt-1">{model.description}</p>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(model.status)}`}>
                  {getStatusIcon(model.status)} {model.status}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <span className="text-sm text-gray-500">Type</span>
                <p className="font-medium text-gray-800">{model.type}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Algorithm</span>
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getAlgorithmColor(model.algorithm)}`}>
                  {model.algorithm}
                </span>
              </div>
              <div>
                <span className="text-sm text-gray-500">Version</span>
                <p className="font-medium text-gray-800">{model.version}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Samples</span>
                <p className="font-medium text-gray-800">{model.training_samples?.toLocaleString()}</p>
              </div>
            </div>

            {/* Performance Metrics */}
            <div className="bg-gray-50 rounded-xl p-4 mb-4">
              <h4 className="font-semibold text-gray-800 mb-3">Performance Metrics</h4>
              <div className="grid grid-cols-2 gap-3">
                {model.accuracy && (
                  <div>
                    <span className="text-xs text-gray-500">Accuracy</span>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full" 
                          style={{ width: `${model.accuracy * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{(model.accuracy * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                )}
                {model.precision && (
                  <div>
                    <span className="text-xs text-gray-500">Precision</span>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full" 
                          style={{ width: `${model.precision * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{(model.precision * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                )}
                {model.recall && (
                  <div>
                    <span className="text-xs text-gray-500">Recall</span>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-purple-500 h-2 rounded-full" 
                          style={{ width: `${model.recall * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{(model.recall * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                )}
                {model.f1_score && (
                  <div>
                    <span className="text-xs text-gray-500">F1 Score</span>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-orange-500 h-2 rounded-full" 
                          style={{ width: `${model.f1_score * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{(model.f1_score * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Features */}
            <div className="mb-4">
              <h4 className="font-semibold text-gray-800 mb-2">Key Features</h4>
              <div className="flex flex-wrap gap-2">
                {model.features?.slice(0, 3).map((feature, index) => (
                  <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    {feature}
                  </span>
                ))}
                {model.features?.length > 3 && (
                  <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                    +{model.features.length - 3} more
                  </span>
                )}
              </div>
            </div>

            {/* Last Trained */}
            <div className="text-xs text-gray-500 mb-4">
              Last trained: {new Date(model.last_trained).toLocaleDateString()}
            </div>

            {/* Actions */}
            <div className="flex space-x-2">
              <button
                onClick={() => handleTrainModel(model.id)}
                disabled={model.status === 'training'}
                className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white px-3 py-2 rounded-lg text-sm font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200 disabled:opacity-50"
              >
                {model.status === 'training' ? 'Training...' : 'Retrain'}
              </button>
              
              {model.status === 'inactive' && (
                <button
                  onClick={() => handleDeployModel(model.id)}
                  className="flex-1 bg-gradient-to-r from-green-500 to-green-600 text-white px-3 py-2 rounded-lg text-sm font-medium hover:from-green-600 hover:to-green-700 transition-all duration-200"
                >
                  Deploy
                </button>
              )}
              
              <button
                onClick={() => setSelectedModel(model)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50 transition-colors"
              >
                Details
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Model Details Modal */}
      {selectedModel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-800">{selectedModel.name}</h2>
              <button
                onClick={() => setSelectedModel(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Description</h3>
                <p className="text-gray-600">{selectedModel.description}</p>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">All Features</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedModel.features?.map((feature, index) => (
                    <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                      {feature}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Performance Details</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(selectedModel).filter(([key, value]) => 
                    ['accuracy', 'precision', 'recall', 'f1_score', 'mae', 'rmse', 'r2_score', 'mape'].includes(key) && value
                  ).map(([key, value]) => (
                    <div key={key} className="bg-gray-50 rounded-lg p-3 text-center">
                      <div className="text-sm text-gray-500 capitalize">{key.replace('_', ' ')}</div>
                      <div className="text-lg font-bold text-gray-800">
                        {typeof value === 'number' ? 
                          (key.includes('score') || key === 'accuracy' || key === 'precision' || key === 'recall' ? 
                            (value * 100).toFixed(1) + '%' : 
                            value.toFixed(3)
                          ) : 
                          value
                        }
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalystModels;
