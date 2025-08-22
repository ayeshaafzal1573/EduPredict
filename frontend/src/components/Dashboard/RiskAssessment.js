import React from 'react';

const RiskAssessment = ({ riskScore = 0.25, riskLevel = 'low' }) => {
  const getRiskColor = (level) => {
    switch (level.toLowerCase()) {
      case 'low':
        return {
          bg: 'from-green-400 to-green-600',
          text: 'text-green-800',
          bgLight: 'bg-green-50',
          border: 'border-green-200',
          icon: '✅'
        };
      case 'medium':
        return {
          bg: 'from-yellow-400 to-yellow-600',
          text: 'text-yellow-800',
          bgLight: 'bg-yellow-50',
          border: 'border-yellow-200',
          icon: '⚠️'
        };
      case 'high':
        return {
          bg: 'from-red-400 to-red-600',
          text: 'text-red-800',
          bgLight: 'bg-red-50',
          border: 'border-red-200',
          icon: '🚨'
        };
      default:
        return {
          bg: 'from-gray-400 to-gray-600',
          text: 'text-gray-800',
          bgLight: 'bg-gray-50',
          border: 'border-gray-200',
          icon: '❓'
        };
    }
  };

  const riskColors = getRiskColor(riskLevel);
  const percentage = Math.round(riskScore * 100);

  const recommendations = {
    low: [
      "Keep up the excellent work! 🎉",
      "Continue attending classes regularly",
      "Maintain your current study habits",
      "Consider helping peers who might be struggling"
    ],
    medium: [
      "Focus on improving attendance",
      "Schedule study sessions with classmates",
      "Meet with your academic advisor",
      "Consider joining study groups"
    ],
    high: [
      "Immediate intervention recommended",
      "Schedule meeting with academic counselor",
      "Consider tutoring services",
      "Review course load and time management"
    ]
  };

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-800">Dropout Risk Assessment</h3>
        <div className="text-2xl">{riskColors.icon}</div>
      </div>

      {/* Risk Score Visualization */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-600">Risk Score</span>
          <span className={`text-lg font-bold ${riskColors.text}`}>
            {percentage}%
          </span>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
          <div 
            className={`h-full bg-gradient-to-r ${riskColors.bg} transition-all duration-1000 ease-out rounded-full relative`}
            style={{ width: `${percentage}%` }}
          >
            <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
          </div>
        </div>
      </div>

      {/* Risk Level Badge */}
      <div className="mb-6">
        <div className={`inline-flex items-center px-4 py-2 rounded-full ${riskColors.bgLight} ${riskColors.border} border`}>
          <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${riskColors.bg} mr-2`}></div>
          <span className={`font-semibold ${riskColors.text} capitalize`}>
            {riskLevel} Risk Level
          </span>
        </div>
      </div>

      {/* AI Insights */}
      <div className="mb-6">
        <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
          <svg className="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          AI-Powered Insights
        </h4>
        <div className="space-y-2">
          {recommendations[riskLevel]?.map((recommendation, index) => (
            <div key={index} className="flex items-start space-x-2">
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-sm text-gray-600">{recommendation}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Action Button */}
      <div className="flex space-x-3">
        <button className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-xl font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105">
          View Detailed Analysis
        </button>
        {riskLevel !== 'low' && (
          <button className="flex-1 bg-white text-gray-700 px-4 py-2 rounded-xl font-medium border border-gray-300 hover:bg-gray-50 transition-all duration-200">
            Get Help
          </button>
        )}
      </div>

      {/* Last Updated */}
      <div className="mt-4 text-xs text-gray-500 text-center">
        Last updated: {new Date().toLocaleDateString()} • Powered by AI
      </div>
    </div>
  );
};

export default RiskAssessment;
