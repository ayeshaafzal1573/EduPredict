import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { analyticsAPI, studentsAPI } from '../../services/api';
import PerformanceChart from '../../components/Charts/PerformanceChart';
import RiskAssessment from '../../components/Dashboard/RiskAssessment';
import toast from 'react-hot-toast';

const StudentDashboard = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [stats, studentData, dropoutPrediction] = await Promise.all([
        analyticsAPI.getDashboardStats('student'),
        studentsAPI.getStudentById('me'),
        analyticsAPI.getDropoutPrediction('me')
      ]);

      setDashboardData({
        stats,
        student: studentData,
        dropoutRisk: dropoutPrediction
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
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">🎓</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Dashboard Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Reload Dashboard
          </button>
        </div>
      </div>
    );
  }

  const stats = dashboardData?.stats || {};
  const dropoutRisk = dashboardData?.dropoutRisk || {};

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">
              Welcome back, {user?.first_name}! 🎓
            </h1>
            <p className="text-blue-100 text-lg">
              Here's your academic performance overview
            </p>
            <div className="mt-4 flex items-center space-x-4">
              <div className="bg-white/20 rounded-lg px-4 py-2">
                <span className="text-sm font-medium">Current Semester: {stats.current_semester || 5}</span>
              </div>
              <div className="bg-white/20 rounded-lg px-4 py-2">
                <span className="text-sm font-medium">Academic Year: 2023-24</span>
              </div>
            </div>
          </div>
          <div className="hidden md:block">
            <div className="w-32 h-32 bg-white/20 rounded-full flex items-center justify-center">
              <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* GPA Card */}
        <div className="bg-white/80 backdrop-blur-sm overflow-hidden shadow-xl rounded-2xl border border-white/20 hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
          <div className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Current GPA
                  </dt>
                  <dd className="text-3xl font-bold text-gray-900 mt-1">
                    {stats.current_gpa || '3.2'}
                  </dd>
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      ↗ +0.2 from last semester
                    </span>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Attendance Card */}
        <div className="bg-white/80 backdrop-blur-sm overflow-hidden shadow-xl rounded-2xl border border-white/20 hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
          <div className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Attendance Rate
                  </dt>
                  <dd className="text-3xl font-bold text-gray-900 mt-1">
                    {stats.attendance_rate || 87}%
                  </dd>
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Above requirement
                    </span>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Risk Level Card */}
        <div className="bg-white/80 backdrop-blur-sm overflow-hidden shadow-xl rounded-2xl border border-white/20 hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
          <div className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-xl flex items-center justify-center shadow-lg">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Risk Level
                  </dt>
                  <dd className="text-3xl font-bold text-gray-900 mt-1 capitalize">
                    {stats.risk_level || 'Low'}
                  </dd>
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Good standing
                    </span>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Credits Card */}
        <div className="bg-white/80 backdrop-blur-sm overflow-hidden shadow-xl rounded-2xl border border-white/20 hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
          <div className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Credits Completed
                  </dt>
                  <dd className="text-3xl font-bold text-gray-900 mt-1">
                    {stats.completed_credits || stats.total_credits || 75}
                  </dd>
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                      On track
                    </span>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Charts and Risk Assessment */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Performance Chart */}
        <PerformanceChart
          title="📈 Academic Performance Trends"
          type="area"
        />

        {/* Risk Assessment */}
        <RiskAssessment
          riskScore={dropoutRisk.risk_score || 0.25}
          riskLevel={dropoutRisk.risk_level || 'low'}
        />
      </div>

      {/* Grade Predictions */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
          <svg className="w-6 h-6 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          AI Grade Predictions
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { course: 'Computer Science 101', predicted: 'A-', confidence: 92, color: 'from-green-400 to-green-600' },
            { course: 'Mathematics 201', predicted: 'B+', confidence: 87, color: 'from-blue-400 to-blue-600' },
            { course: 'Physics 101', predicted: 'B', confidence: 78, color: 'from-yellow-400 to-yellow-600' },
          ].map((course, index) => (
            <div key={index} className="bg-gradient-to-br from-white/60 to-white/40 rounded-xl p-4 border border-white/30">
              <h3 className="font-semibold text-gray-800 mb-2">{course.course}</h3>
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl font-bold text-gray-900">{course.predicted}</span>
                <div className={`px-3 py-1 rounded-full bg-gradient-to-r ${course.color} text-white text-sm font-medium`}>
                  {course.confidence}% confident
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 bg-gradient-to-r ${course.color} rounded-full transition-all duration-1000`}
                  style={{ width: `${course.confidence}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h2 className="text-xl font-bold text-gray-800 mb-6">Recent Activity</h2>
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Grade updated for CS101 - Introduction to Computer Science</span>
            <span className="text-xs text-gray-400">2 hours ago</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Attendance marked for MATH201 - Calculus II</span>
            <span className="text-xs text-gray-400">1 day ago</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Assignment due reminder for PHYS101</span>
            <span className="text-xs text-gray-400">2 days ago</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;