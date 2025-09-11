import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { analyticsAPI } from '../../services/api';
import PerformanceChart from '../../components/Charts/PerformanceChart';
import toast from 'react-hot-toast';

const AnalystDashboard = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMetric, setSelectedMetric] = useState('overview');

  useEffect(() => {
    fetchDashboardData();
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [institutionAnalytics, atRiskStudents] = await Promise.all([
        analyticsAPI.getInstitutionAnalytics(),
        analyticsAPI.getAtRiskStudents(50)
      ]);

      setDashboardData({
        institution: institutionAnalytics,
        atRiskStudents,
        modelMetrics: {
          dropoutModel: { accuracy: 87.2, precision: 84.5, recall: 89.1, f1Score: 86.7 },
          gradeModel: { accuracy: 82.4, mae: 0.23, rmse: 0.31, r2Score: 0.78 }
        },
        dataStats: {
          totalRecords: 125000,
          processedToday: 2450,
          predictionsMade: 1850,
          modelsActive: 4
        }
      });
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data. Please try again.');
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analyst dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">📊</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Dashboard Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Reload Dashboard
          </button>
        </div>
      </div>
    );
  }

  const { institution, atRiskStudents, modelMetrics, dataStats } = dashboardData;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">
          Welcome, {user?.first_name}! 📊
        </h1>
        <p className="text-purple-100 text-lg">
          Advanced analytics and machine learning insights
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">ML Model Accuracy</p>
              <p className="text-3xl font-bold">{modelMetrics.dropoutModel.accuracy}%</p>
            </div>
            <div className="text-4xl opacity-80">🎯</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Predictions Made</p>
              <p className="text-3xl font-bold">{dataStats.predictionsMade.toLocaleString()}</p>
            </div>
            <div className="text-4xl opacity-80">🔮</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Data Points</p>
              <p className="text-3xl font-bold">{(dataStats.totalRecords / 1000).toFixed(0)}K</p>
            </div>
            <div className="text-4xl opacity-80">📈</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">Active Models</p>
              <p className="text-3xl font-bold">{dataStats.modelsActive}</p>
            </div>
            <div className="text-4xl opacity-80">🤖</div>
          </div>
        </div>
      </div>

      {/* Analytics Tabs */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', name: 'Overview', icon: '📊' },
              { id: 'models', name: 'ML Models', icon: '🤖' },
              { id: 'predictions', name: 'Predictions', icon: '🔮' },
              { id: 'insights', name: 'Insights', icon: '💡' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedMetric(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  selectedMetric === tab.id
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {selectedMetric === 'overview' && (
            <div className="space-y-6">
              <h3 className="text-xl font-bold text-gray-800">Analytics Overview</h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6">
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Department Performance</h4>
                  <div className="space-y-3">
                    {institution.department_distribution?.map((dept, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-gray-700">{dept.name}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-purple-500 h-2 rounded-full"
                              style={{ width: `${(dept.count / 100 * 100)}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium text-gray-600">{dept.count}</span>
                        </div>
                      </div>
                    )) || (
                      <p className="text-gray-500">No department data available</p>
                    )}
                  </div>
                </div>

                <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6">
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Risk Distribution</h4>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-700">Low Risk</span>
                      <span className="text-green-600 font-semibold">75%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-700">Medium Risk</span>
                      <span className="text-yellow-600 font-semibold">18%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-700">High Risk</span>
                      <span className="text-red-600 font-semibold">7%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {selectedMetric === 'models' && (
            <div className="space-y-6">
              <h3 className="text-xl font-bold text-gray-800">Machine Learning Models</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Dropout Prediction Model</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Accuracy</span>
                      <span className="font-semibold text-green-600">{modelMetrics.dropoutModel.accuracy}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Precision</span>
                      <span className="font-semibold text-blue-600">{modelMetrics.dropoutModel.precision}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Recall</span>
                      <span className="font-semibold text-purple-600">{modelMetrics.dropoutModel.recall}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">F1 Score</span>
                      <span className="font-semibold text-orange-600">{modelMetrics.dropoutModel.f1Score}%</span>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Grade Prediction Model</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Accuracy</span>
                      <span className="font-semibold text-green-600">{modelMetrics.gradeModel.accuracy}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">MAE</span>
                      <span className="font-semibold text-blue-600">{modelMetrics.gradeModel.mae}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">RMSE</span>
                      <span className="font-semibold text-purple-600">{modelMetrics.gradeModel.rmse}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">R² Score</span>
                      <span className="font-semibold text-orange-600">{modelMetrics.gradeModel.r2Score}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {selectedMetric === 'predictions' && (
            <div className="space-y-6">
              <h3 className="text-xl font-bold text-gray-800">Recent Predictions</h3>
              
              <div className="bg-white rounded-xl p-6 shadow-lg">
                <h4 className="text-lg font-semibold text-gray-800 mb-4">High-Risk Students</h4>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {atRiskStudents.slice(0, 10).map((student, index) => (
                    <div key={index} className="p-3 bg-red-50 rounded-lg border border-red-200">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-800">{student.student_name}</div>
                          <div className="text-sm text-red-600">
                            GPA: {student.gpa} | Attendance: {student.attendance_rate}%
                          </div>
                        </div>
                        <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                          {student.risk_level}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {selectedMetric === 'insights' && (
            <div className="space-y-6">
              <h3 className="text-xl font-bold text-gray-800">AI Insights</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-xl p-6 shadow-lg">
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Key Findings</h4>
                  <div className="space-y-3">
                    <div className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                      <div>
                        <p className="font-medium text-gray-900">Attendance Impact</p>
                        <p className="text-sm text-gray-600">Students with >90% attendance have 85% lower dropout risk</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                      <div>
                        <p className="font-medium text-gray-900">Early Warning</p>
                        <p className="text-sm text-gray-600">First semester GPA is the strongest predictor of graduation</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
                      <div>
                        <p className="font-medium text-gray-900">Intervention Success</p>
                        <p className="text-sm text-gray-600">Early interventions improve retention by 23%</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-xl p-6 shadow-lg">
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Recommendations</h4>
                  <div className="space-y-3">
                    <div className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
                      <div>
                        <p className="font-medium text-gray-900">Focus on STEM</p>
                        <p className="text-sm text-gray-600">STEM courses show higher dropout rates - increase support</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
                      <div>
                        <p className="font-medium text-gray-900">Attendance Monitoring</p>
                        <p className="text-sm text-gray-600">Implement automated attendance alerts</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-indigo-500 rounded-full mt-2"></div>
                      <div>
                        <p className="font-medium text-gray-900">Model Retraining</p>
                        <p className="text-sm text-gray-600">Schedule monthly model updates with new data</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Performance Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <PerformanceChart
          title="📈 Institution Performance Trends"
          data={institution.gpa_trends}
          type="area"
        />

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <h3 className="text-xl font-bold text-gray-800 mb-6">Model Performance Over Time</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl">
              <div>
                <div className="font-semibold text-blue-900">Dropout Model</div>
                <div className="text-sm text-blue-700">Random Forest Classifier</div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-blue-900">{modelMetrics.dropoutModel.accuracy}%</div>
                <div className="text-sm text-blue-700">Accuracy</div>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-green-100 rounded-xl">
              <div>
                <div className="font-semibold text-green-900">Grade Model</div>
                <div className="text-sm text-green-700">Random Forest Regressor</div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-green-900">{modelMetrics.gradeModel.accuracy}%</div>
                <div className="text-sm text-green-700">Accuracy</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Data Processing Stats */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h3 className="text-xl font-bold text-gray-800 mb-6">Data Processing Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{dataStats.totalRecords.toLocaleString()}</div>
            <div className="text-sm text-gray-600">Total Records</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">{dataStats.processedToday.toLocaleString()}</div>
            <div className="text-sm text-gray-600">Processed Today</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">{dataStats.predictionsMade.toLocaleString()}</div>
            <div className="text-sm text-gray-600">Predictions Made</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">99.2%</div>
            <div className="text-sm text-gray-600">System Uptime</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalystDashboard;