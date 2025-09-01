import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { analyticsAPI } from '../../services/api';
import PerformanceChart from '../../components/Charts/PerformanceChart';
import toast from 'react-hot-toast';

const AdminAnalytics = () => {
  const { user } = useAuth();
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMetric, setSelectedMetric] = useState('overview');

  useEffect(() => {
    fetchAnalyticsData();
  }, [user]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Always fetch from APIs - no fallback data in frontend
      const [dashboardStats, institutionAnalytics, atRiskStudents] = await Promise.all([
        analyticsAPI.getDashboardStats('admin'),
        analyticsAPI.getInstitutionAnalytics(),
        analyticsAPI.getAtRiskStudents(20)
      ]);

      setAnalyticsData({
        dashboard: dashboardStats,
        institution: institutionAnalytics,
        atRiskStudents
      });
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError('Failed to load analytics data. Please try again.');
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">📊</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Analytics Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchAnalyticsData}
            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Reload Analytics
          </button>
        </div>
      </div>
    );
  }

  const dashboardStats = analyticsData?.dashboard || {};
  const institutionData = analyticsData?.institution || {};
  const atRiskStudents = analyticsData?.atRiskStudents || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-600 to-pink-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">📊 Institution Analytics</h1>
        <p className="text-red-100 text-lg">
          Comprehensive analytics and insights for institutional management
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Total Students</p>
              <p className="text-3xl font-bold">{dashboardStats.total_students || 0}</p>
              <p className="text-blue-200 text-xs mt-1">
                +{dashboardStats.new_students_this_month || 0} this month
              </p>
            </div>
            <div className="text-4xl opacity-80">👥</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Average GPA</p>
              <p className="text-3xl font-bold">{dashboardStats.average_gpa || '0.0'}</p>
              <p className="text-green-200 text-xs mt-1">
                {dashboardStats.gpa_trend > 0 ? '+' : ''}{dashboardStats.gpa_trend || 0}% from last semester
              </p>
            </div>
            <div className="text-4xl opacity-80">📈</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-500 to-orange-500 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100 text-sm">Attendance Rate</p>
              <p className="text-3xl font-bold">{dashboardStats.attendance_rate || 0}%</p>
              <p className="text-yellow-200 text-xs mt-1">
                Institution average
              </p>
            </div>
            <div className="text-4xl opacity-80">📅</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-pink-500 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-100 text-sm">At-Risk Students</p>
              <p className="text-3xl font-bold">{atRiskStudents.length}</p>
              <p className="text-red-200 text-xs mt-1">
                Need immediate attention
              </p>
            </div>
            <div className="text-4xl opacity-80">⚠️</div>
          </div>
        </div>
      </div>

      {/* Analytics Tabs */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', name: 'Overview', icon: '📊' },
              { id: 'performance', name: 'Performance', icon: '📈' },
              { id: 'enrollment', name: 'Enrollment', icon: '🎓' },
              { id: 'risk', name: 'Risk Analysis', icon: '⚠️' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedMetric(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${selectedMetric === tab.id
                  ? 'border-red-500 text-red-600'
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
              <h3 className="text-xl font-bold text-gray-800">Institution Overview</h3>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6">
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Department Distribution</h4>
                  <div className="space-y-3">
                    {institutionData.department_distribution?.map((dept, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-gray-700">{dept.name}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-red-500 h-2 rounded-full"
                              style={{ width: `${(dept.count / dashboardStats.total_students * 100)}%` }}
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
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Academic Performance</h4>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-700">Excellent (A)</span>
                      <span className="text-green-600 font-semibold">{institutionData.grade_distribution?.A || 0}%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-700">Good (B)</span>
                      <span className="text-blue-600 font-semibold">{institutionData.grade_distribution?.B || 0}%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-700">Average (C)</span>
                      <span className="text-yellow-600 font-semibold">{institutionData.grade_distribution?.C || 0}%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-700">Below Average (D/F)</span>
                      <span className="text-red-600 font-semibold">{(institutionData.grade_distribution?.D || 0) + (institutionData.grade_distribution?.F || 0)}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {selectedMetric === 'performance' && (
            <div className="space-y-6">
              <h3 className="text-xl font-bold text-gray-800">Performance Analytics</h3>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-xl p-6 shadow-lg">
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">GPA Trends</h4>
                  <PerformanceChart
                    data={institutionData.gpa_trends || []}
                    title="Institution GPA Over Time"
                  />
                </div>

                <div className="bg-white rounded-xl p-6 shadow-lg">
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Top Performing Courses</h4>
                  <div className="space-y-3">
                    {institutionData.top_courses?.slice(0, 5).map((course, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <div className="font-medium text-gray-800">{course.name}</div>
                          <div className="text-sm text-gray-500">{course.code}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold text-gray-800">{course.average_gpa}</div>
                          <div className="text-sm text-gray-500">{course.student_count} students</div>
                        </div>
                      </div>
                    )) || (
                        <p className="text-gray-500">No course performance data available</p>
                      )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {selectedMetric === 'enrollment' && (
            <div className="space-y-6">
              <h3 className="text-xl font-bold text-gray-800">Enrollment Analytics</h3>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6">
                  <h4 className="text-lg font-semibold text-blue-800 mb-2">Total Enrollment</h4>
                  <div className="text-3xl font-bold text-blue-900 mb-2">
                    {dashboardStats.total_students || 0}
                  </div>
                  <p className="text-blue-700 text-sm">
                    +{dashboardStats.enrollment_growth || 0}% from last year
                  </p>
                </div>

                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6">
                  <h4 className="text-lg font-semibold text-green-800 mb-2">Active Courses</h4>
                  <div className="text-3xl font-bold text-green-900 mb-2">
                    {dashboardStats.active_courses || 0}
                  </div>
                  <p className="text-green-700 text-sm">Across all departments</p>
                </div>

                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6">
                  <h4 className="text-lg font-semibold text-purple-800 mb-2">Faculty</h4>
                  <div className="text-3xl font-bold text-purple-900 mb-2">
                    {dashboardStats.total_teachers || 0}
                  </div>
                  <p className="text-purple-700 text-sm">Active teaching staff</p>
                </div>
              </div>
            </div>
          )}

          {selectedMetric === 'risk' && (
            <div className="space-y-6">
              <h3 className="text-xl font-bold text-gray-800">Risk Analysis</h3>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-xl p-6 shadow-lg">
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">At-Risk Students</h4>
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
                        <div className="mt-2 text-xs text-red-700">
                          {student.risk_factors?.slice(0, 2).join(', ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-white rounded-xl p-6 shadow-lg">
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Risk Factors Distribution</h4>
                  <div className="space-y-4">
                    {institutionData.risk_factors?.map((factor, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-gray-700">{factor.name}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-red-500 h-2 rounded-full"
                              style={{ width: `${factor.percentage}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium text-gray-600">{factor.percentage}%</span>
                        </div>
                      </div>
                    )) || (
                        <p className="text-gray-500">No risk factor data available</p>
                      )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminAnalytics;
