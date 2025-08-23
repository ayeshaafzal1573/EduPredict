import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { analyticsAPI, coursesAPI } from '../../services/api';
import PerformanceChart from '../../components/Charts/PerformanceChart';
import toast from 'react-hot-toast';

const TeacherAnalytics = () => {
  const { user } = useAuth();
  const [analyticsData, setAnalyticsData] = useState(null);
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [teacherCourses, dashboardStats] = await Promise.all([
        coursesAPI.getCourses({ teacher_id: user.id }),
        analyticsAPI.getDashboardStats('teacher')
      ]);

      setCourses(teacherCourses);
      if (teacherCourses.length > 0) {
        setSelectedCourse(teacherCourses[0]);
        const classAnalytics = await analyticsAPI.getClassAnalytics(teacherCourses[0].id);
        setAnalyticsData({
          dashboard: dashboardStats,
          classData: classAnalytics
        });
      } else {
        setAnalyticsData({ dashboard: dashboardStats, classData: null });
      }
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError('Failed to load analytics data. Please try again.');
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const handleCourseChange = async (course) => {
    try {
      setSelectedCourse(course);
      const classAnalytics = await analyticsAPI.getClassAnalytics(course.id);
      setAnalyticsData(prev => ({
        ...prev,
        classData: classAnalytics
      }));
    } catch (err) {
      console.error('Error fetching class analytics:', err);
      toast.error('Failed to load class analytics');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
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
            onClick={fetchData}
            className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Reload Analytics
          </button>
        </div>
      </div>
    );
  }

  const dashboardStats = analyticsData?.dashboard || {};
  const classData = analyticsData?.classData || {};

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">📊 Teaching Analytics</h1>
        <p className="text-green-100 text-lg">
          Analyze student performance and class insights
        </p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Total Students</p>
              <p className="text-3xl font-bold">{dashboardStats.total_students || 0}</p>
            </div>
            <div className="text-4xl opacity-80">👥</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Average Grade</p>
              <p className="text-3xl font-bold">{dashboardStats.average_grade || 'N/A'}</p>
            </div>
            <div className="text-4xl opacity-80">📈</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-500 to-orange-500 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100 text-sm">Attendance Rate</p>
              <p className="text-3xl font-bold">{dashboardStats.attendance_rate || 0}%</p>
            </div>
            <div className="text-4xl opacity-80">📅</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-pink-500 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-100 text-sm">At-Risk Students</p>
              <p className="text-3xl font-bold">{dashboardStats.at_risk_students || 0}</p>
            </div>
            <div className="text-4xl opacity-80">⚠️</div>
          </div>
        </div>
      </div>

      {/* Course Selection */}
      {courses.length > 0 && (
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Select Course for Detailed Analytics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {courses.map((course) => (
              <button
                key={course.id}
                onClick={() => handleCourseChange(course)}
                className={`p-4 rounded-xl border-2 transition-all duration-200 text-left ${
                  selectedCourse?.id === course.id
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <h3 className="font-semibold text-gray-800">{course.name}</h3>
                <p className="text-sm text-gray-600">{course.code}</p>
                <p className="text-xs text-gray-500">{course.student_count || 0} students</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Class Analytics */}
      {selectedCourse && classData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Grade Distribution</h3>
            <div className="space-y-3">
              {Object.entries(classData.grade_distribution || {}).map(([grade, count]) => (
                <div key={grade} className="flex items-center justify-between">
                  <span className="text-gray-700">Grade {grade}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full" 
                        style={{ width: `${(count / (classData.total_students || 1)) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-600">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Performance Trends</h3>
            <PerformanceChart 
              data={classData.performance_trends || []}
              title="Class Performance Over Time"
            />
          </div>
        </div>
      )}

      {/* At-Risk Students */}
      {classData?.at_risk_students && classData.at_risk_students.length > 0 && (
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Students Needing Attention</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {classData.at_risk_students.map((student, index) => (
              <div key={index} className="p-4 bg-red-50 rounded-xl border border-red-200">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center text-white font-semibold">
                    {student.name?.split(' ').map(n => n[0]).join('') || 'S'}
                  </div>
                  <div>
                    <div className="font-medium text-gray-800">{student.name}</div>
                    <div className="text-sm text-red-600">
                      GPA: {student.gpa} | Attendance: {student.attendance_rate}%
                    </div>
                  </div>
                </div>
                <div className="mt-2">
                  <div className="text-xs text-red-700">
                    Risk Factors: {student.risk_factors?.join(', ') || 'Multiple factors'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {courses.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📊</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No courses assigned</h3>
          <p className="text-gray-500">You don't have any courses assigned yet to analyze.</p>
        </div>
      )}
    </div>
  );
};

export default TeacherAnalytics;
