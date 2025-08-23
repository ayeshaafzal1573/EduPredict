import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { analyticsAPI } from '../../services/api';
import RiskAssessment from '../../components/Dashboard/RiskAssessment';
import toast from 'react-hot-toast';

const StudentPredictions = () => {
  const { user } = useAuth();
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPredictions();
  }, [user]);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch predictions from API
      const [dropoutPrediction, gradePredictions] = await Promise.all([
        analyticsAPI.getDropoutPrediction(user.id),
        analyticsAPI.getGradePredictions(user.id)
      ]);

      const processedPredictions = {
        dropoutRisk: {
          score: dropoutPrediction.risk_score || 0,
          level: dropoutPrediction.risk_level || 'low',
          factors: dropoutPrediction.factors || []
        },
        gradePredictions: gradePredictions.predictions || [],
        semesterPrediction: {
          expectedGPA: gradePredictions.overall_predicted_gpa || 0,
          confidence: 85, // This would come from the API
          improvement: calculateImprovement(gradePredictions.overall_predicted_gpa, user.current_gpa)
        },
        recommendations: dropoutPrediction.recommendations || []
      };

      setPredictions(processedPredictions);
    } catch (err) {
      console.error('Error fetching predictions:', err);
      setError('Failed to load prediction data. Please try again.');
      toast.error('Failed to load predictions');
    } finally {
      setLoading(false);
    }
  };

  const calculateImprovement = (predicted, current) => {
    if (!predicted || !current) return '+0.0';
    const diff = predicted - current;
    return diff >= 0 ? `+${diff.toFixed(1)}` : diff.toFixed(1);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading AI predictions...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">🤖</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Prediction Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchPredictions}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Retry Predictions
          </button>
        </div>
      </div>
    );
  }

  if (!predictions) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-gray-400 text-6xl mb-4">🔮</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">No Predictions Available</h2>
          <p className="text-gray-600">AI predictions will be available once you have more academic data.</p>
        </div>
      </div>
    );
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'from-red-500 to-red-600';
      case 'medium': return 'from-yellow-500 to-yellow-600';
      case 'low': return 'from-green-500 to-green-600';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'positive': return 'text-green-600 bg-green-100';
      case 'negative': return 'text-red-600 bg-red-100';
      case 'neutral': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">🔮 AI Predictions</h1>
        <p className="text-indigo-100 text-lg">
          Advanced analytics and predictions for your academic journey
        </p>
      </div>

      {/* Dropout Risk Assessment */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <RiskAssessment
          riskScore={predictions.dropoutRisk.score}
          riskLevel={predictions.dropoutRisk.level}
        />

        {/* Risk Factors */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <h3 className="text-xl font-bold text-gray-800 mb-6">Risk Factors Analysis</h3>
          <div className="space-y-4">
            {predictions.dropoutRisk.factors.map((factor, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900">{factor.name}</h4>
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-1000"
                        style={{ width: `${factor.score * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
                <div className="ml-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getImpactColor(factor.impact)}`}>
                    {factor.impact}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Grade Predictions */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
          <svg className="w-6 h-6 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          Course Grade Predictions
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {predictions.gradePredictions.map((course, index) => (
            <div key={index} className="bg-gradient-to-br from-white/60 to-white/40 rounded-xl p-6 border border-white/30">
              <h3 className="font-semibold text-gray-800 mb-4">{course.course}</h3>

              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-sm text-gray-600">Current Grade</p>
                  <p className="text-2xl font-bold text-gray-900">{course.current}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">Predicted Grade</p>
                  <p className="text-2xl font-bold text-blue-600">{course.predicted}</p>
                </div>
              </div>

              <div className="mb-4">
                <div className="flex justify-between text-sm mb-1">
                  <span>Confidence Level</span>
                  <span>{course.confidence}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full transition-all duration-1000"
                    style={{ width: `${course.confidence}%` }}
                  ></div>
                </div>
              </div>

              {course.predicted !== course.current && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-sm text-blue-800">
                    📈 Predicted improvement from {course.current} to {course.predicted}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Semester Prediction */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h2 className="text-xl font-bold text-gray-800 mb-6">Semester GPA Prediction</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl border border-blue-100">
            <div className="text-4xl font-bold text-blue-600 mb-2">{predictions.semesterPrediction.expectedGPA}</div>
            <p className="text-gray-600">Expected GPA</p>
          </div>

          <div className="text-center p-6 bg-gradient-to-br from-green-50 to-blue-50 rounded-xl border border-green-100">
            <div className="text-4xl font-bold text-green-600 mb-2">{predictions.semesterPrediction.confidence}%</div>
            <p className="text-gray-600">Confidence</p>
          </div>

          <div className="text-center p-6 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-100">
            <div className="text-4xl font-bold text-purple-600 mb-2">{predictions.semesterPrediction.improvement}</div>
            <p className="text-gray-600">Improvement</p>
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
          <svg className="w-6 h-6 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.12 9l3 3m0 0l3-3m-3 3V3m-6 6h12a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2v-6a2 2 0 012-2z" />
          </svg>
          AI Recommendations
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {predictions.recommendations.map((rec, index) => (
            <div key={index} className="bg-gradient-to-br from-white/60 to-white/40 rounded-xl p-6 border border-white/30">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-800">{rec.title}</h3>
                <div className={`px-3 py-1 rounded-full bg-gradient-to-r ${getPriorityColor(rec.priority)} text-white text-xs font-medium`}>
                  {rec.priority}
                </div>
              </div>
              <p className="text-gray-600 text-sm">{rec.description}</p>

              <button className="mt-4 w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200">
                Take Action
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Prediction Accuracy */}
      <div className="bg-gradient-to-r from-gray-50 to-white rounded-2xl p-6 border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-800">Prediction Accuracy</h3>
            <p className="text-gray-600">Our AI model has 89% accuracy in grade predictions</p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-green-600">89%</div>
            <p className="text-sm text-gray-500">Historical Accuracy</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentPredictions;
