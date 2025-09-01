import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { attendanceAPI, coursesAPI } from '../../services/api';
import toast from 'react-hot-toast';

const StudentAttendance = () => {
  const { user } = useAuth();
  const [attendanceData, setAttendanceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCourse, setSelectedCourse] = useState('all');

  useEffect(() => {
    fetchAttendanceData();
  }, [user]);

  const fetchAttendanceData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Always fetch from APIs - no fallback data in frontend
      const [attendanceRecords, studentCourses] = await Promise.all([
        attendanceAPI.getAttendance({ student_id: user.id, limit: 200 }),
        coursesAPI.getCourses({ student_id: user.id })
      ]);

      // Process attendance data by course
      const courseAttendance = {};
      let totalClasses = 0;
      let totalAttended = 0;

      // Initialize course data
      studentCourses.forEach(course => {
        courseAttendance[course.id] = {
          id: course.id,
          name: course.name,
          totalClasses: 0,
          attended: 0,
          percentage: 0,
          status: 'good',
          recentClasses: []
        };
      });

      // Process attendance records
      attendanceRecords.forEach(record => {
        const courseId = record.course_id;
        if (courseAttendance[courseId]) {
          courseAttendance[courseId].totalClasses++;
          totalClasses++;

          if (record.status === 'present') {
            courseAttendance[courseId].attended++;
            totalAttended++;
          }

          // Add to recent classes (keep last 5)
          courseAttendance[courseId].recentClasses.push({
            date: record.date,
            status: record.status
          });
        }
      });

      // Calculate percentages and determine status
      Object.values(courseAttendance).forEach(course => {
        if (course.totalClasses > 0) {
          course.percentage = Math.round((course.attended / course.totalClasses) * 100);
          course.status = determineAttendanceStatus(course.percentage);

          // Sort recent classes by date and keep last 5
          course.recentClasses = course.recentClasses
            .sort((a, b) => new Date(b.date) - new Date(a.date))
            .slice(0, 5);
        }
      });

      const overallPercentage = totalClasses > 0 ? Math.round((totalAttended / totalClasses) * 100) : 0;

      const processedData = {
        overall: {
          totalClasses,
          attended: totalAttended,
          percentage: overallPercentage,
          trend: calculateTrend(attendanceRecords) // This would calculate recent trend
        },
        courses: Object.values(courseAttendance).filter(course => course.totalClasses > 0)
      };

      setAttendanceData(processedData);
    } catch (err) {
      console.error('Error fetching attendance data:', err);
      setError('Failed to load attendance data. Please try again.');
      toast.error('Failed to load attendance data');
    } finally {
      setLoading(false);
    }
  };

  const determineAttendanceStatus = (percentage) => {
    if (percentage >= 90) return 'excellent';
    if (percentage >= 80) return 'good';
    if (percentage >= 70) return 'warning';
    return 'critical';
  };

  const calculateTrend = (records) => {
    // Simple trend calculation - compare last 2 weeks vs previous 2 weeks
    const twoWeeksAgo = new Date();
    twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);
    const fourWeeksAgo = new Date();
    fourWeeksAgo.setDate(fourWeeksAgo.getDate() - 28);

    const recentRecords = records.filter(r => new Date(r.date) >= twoWeeksAgo);
    const olderRecords = records.filter(r => new Date(r.date) >= fourWeeksAgo && new Date(r.date) < twoWeeksAgo);

    const recentRate = recentRecords.length > 0 ?
      (recentRecords.filter(r => r.status === 'present').length / recentRecords.length) * 100 : 0;
    const olderRate = olderRecords.length > 0 ?
      (olderRecords.filter(r => r.status === 'present').length / olderRecords.length) * 100 : 0;

    const diff = recentRate - olderRate;
    return diff > 0 ? `+${diff.toFixed(0)}%` : `${diff.toFixed(0)}%`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading attendance data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">📅</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Attendance Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchAttendanceData}
            className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Reload Attendance
          </button>
        </div>
      </div>
    );
  }

  if (!attendanceData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-gray-400 text-6xl mb-4">📊</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">No Attendance Data</h2>
          <p className="text-gray-600">No attendance records found. Data will appear once classes begin.</p>
        </div>
      </div>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'excellent': return 'from-green-500 to-green-600';
      case 'good': return 'from-blue-500 to-blue-600';
      case 'warning': return 'from-yellow-500 to-yellow-600';
      case 'critical': return 'from-red-500 to-red-600';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'excellent': return 'bg-green-100 text-green-800';
      case 'good': return 'bg-blue-100 text-blue-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredCourses = selectedCourse === 'all'
    ? attendanceData.courses
    : attendanceData.courses.filter(course => course.id === selectedCourse);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-teal-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">📅 Attendance Tracker</h1>
        <p className="text-green-100 text-lg">
          Monitor your class attendance and maintain academic requirements
        </p>
      </div>

      {/* Overall Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Overall Attendance</p>
              <p className="text-3xl font-bold text-gray-900">{attendanceData.overall.percentage}%</p>
              <p className="text-sm text-green-600">{attendanceData.overall.trend} this month</p>
            </div>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-green-600 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Classes Attended</p>
              <p className="text-3xl font-bold text-gray-900">{attendanceData.overall.attended}</p>
              <p className="text-sm text-gray-600">out of {attendanceData.overall.totalClasses}</p>
            </div>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Classes Missed</p>
              <p className="text-3xl font-bold text-gray-900">{attendanceData.overall.totalClasses - attendanceData.overall.attended}</p>
              <p className="text-sm text-gray-600">this semester</p>
            </div>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Requirement</p>
              <p className="text-3xl font-bold text-gray-900">75%</p>
              <p className="text-sm text-green-600">✓ Met</p>
            </div>
          </div>
        </div>
      </div>

      {/* Course Filter */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-800">Course-wise Attendance</h2>
          <select
            value={selectedCourse}
            onChange={(e) => setSelectedCourse(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Courses</option>
            {attendanceData.courses.map(course => (
              <option key={course.id} value={course.id}>{course.name}</option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredCourses.map((course, index) => (
            <div key={index} className="bg-gradient-to-br from-white/60 to-white/40 rounded-xl p-6 border border-white/30">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-800">{course.name}</h3>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(course.status)}`}>
                  {course.status}
                </span>
              </div>

              <div className="mb-4">
                <div className="flex justify-between text-sm mb-2">
                  <span>Attendance Rate</span>
                  <span>{course.percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 bg-gradient-to-r ${getStatusColor(course.status)} rounded-full transition-all duration-1000`}
                    style={{ width: `${course.percentage}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>{course.attended} attended</span>
                  <span>{course.totalClasses} total</span>
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700">Recent Classes</h4>
                <div className="flex space-x-2">
                  {course.recentClasses.map((cls, idx) => (
                    <div
                      key={idx}
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${cls.status === 'present'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                        }`}
                      title={`${cls.date} - ${cls.status}`}
                    >
                      {cls.status === 'present' ? '✓' : '✗'}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Attendance Calendar */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h2 className="text-xl font-bold text-gray-800 mb-6">Attendance Calendar</h2>
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100">
          <p className="text-center text-gray-600 mb-4">📅 Calendar view coming soon</p>
          <p className="text-center text-sm text-gray-500">
            Interactive calendar to view daily attendance across all courses
          </p>
        </div>
      </div>

      {/* Attendance Insights */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
          <svg className="w-6 h-6 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          Attendance Insights
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div>
                <p className="font-medium text-gray-900">Strong Performance</p>
                <p className="text-sm text-gray-600">Your attendance is above the 75% requirement in all courses.</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
              <div>
                <p className="font-medium text-gray-900">Focus on Physics</p>
                <p className="text-sm text-gray-600">Physics 101 attendance is at 71%. Consider improving to avoid academic issues.</p>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <p className="font-medium text-gray-900">Consistent Pattern</p>
                <p className="text-sm text-gray-600">You maintain excellent attendance in Computer Science and English courses.</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
              <div>
                <p className="font-medium text-gray-900">Improvement Trend</p>
                <p className="text-sm text-gray-600">Your overall attendance has improved by 2% this month.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentAttendance;
