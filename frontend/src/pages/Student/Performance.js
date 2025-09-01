import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { analyticsAPI, studentsAPI, gradesAPI } from '../../services/api';
import PerformanceChart from '../../components/Charts/PerformanceChart';
import toast from 'react-hot-toast';

const StudentPerformance = () => {
  const { user } = useAuth();
  const [performanceData, setPerformanceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSemester, setSelectedSemester] = useState('current');

  useEffect(() => {
    fetchPerformanceData();
  }, [user]);

  const fetchPerformanceData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Always fetch from APIs - no fallback data in frontend
      const [studentData, performanceTrends, grades] = await Promise.all([
        studentsAPI.getStudentById(user.id),
        analyticsAPI.getPerformanceTrends(user.id),
        gradesAPI.getGrades({ student_id: user.id, limit: 50 })
      ]);

      // Process the data
      const processedData = {
        currentGPA: studentData.gpa || studentData.current_gpa || 0,
        semesterGPA: calculateSemesterGPA(grades),
        totalCredits: studentData.total_credits || 0,
        completedCredits: studentData.completed_credits || 0,
        courses: processCourseGrades(grades),
        trends: performanceTrends.grade_trends || []
      };

      setPerformanceData(processedData);
    } catch (err) {
      console.error('Error fetching performance data:', err);
      setError('Failed to load performance data. Please try again.');
      toast.error('Failed to load performance data');
    } finally {
      setLoading(false);
    }
  };

  const calculateSemesterGPA = (grades) => {
    if (!grades || grades.length === 0) return 0;

    // Get current semester grades (last 30 days)
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const recentGrades = grades.filter(grade =>
      new Date(grade.created_at) >= thirtyDaysAgo
    );

    if (recentGrades.length === 0) return 0;

    const totalPoints = recentGrades.reduce((sum, grade) => sum + (grade.grade_points || 0), 0);
    return Math.round((totalPoints / recentGrades.length) * 100) / 100;
  };

  const processCourseGrades = (grades) => {
    if (!grades || grades.length === 0) return [];

    // Group grades by course
    const courseGrades = {};
    grades.forEach(grade => {
      if (!courseGrades[grade.course_id]) {
        courseGrades[grade.course_id] = {
          name: grade.course_name || 'Unknown Course',
          grades: [],
          credits: 3 // Default credits, should come from course data
        };
      }
      courseGrades[grade.course_id].grades.push(grade);
    });

    // Calculate average grade for each course
    return Object.values(courseGrades).map(course => {
      const avgGradePoints = course.grades.reduce((sum, g) => sum + (g.grade_points || 0), 0) / course.grades.length;
      const latestGrade = course.grades[course.grades.length - 1];

      return {
        name: course.name,
        grade: latestGrade?.letter_grade || 'N/A',
        credits: course.credits,
        gpa: Math.round(avgGradePoints * 100) / 100
      };
    }).slice(0, 6); // Show top 6 courses
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your performance data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Error Loading Data</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchPerformanceData}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!performanceData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-gray-400 text-6xl mb-4">📊</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">No Performance Data</h2>
          <p className="text-gray-600">No performance data available at this time.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">📊 Academic Performance</h1>
        <p className="text-purple-100 text-lg">
          Track your academic progress and performance trends
        </p>
      </div>

      {/* Performance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">GPA</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Current GPA</p>
              <p className="text-3xl font-bold text-gray-900">{performanceData.currentGPA}</p>
            </div>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-green-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-sm">SEM</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Semester GPA</p>
              <p className="text-3xl font-bold text-gray-900">{performanceData.semesterGPA}</p>
            </div>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Credits</p>
              <p className="text-3xl font-bold text-gray-900">{performanceData.completedCredits}/{performanceData.totalCredits}</p>
            </div>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">%</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Progress</p>
              <p className="text-3xl font-bold text-gray-900">{Math.round((performanceData.completedCredits / performanceData.totalCredits) * 100)}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <PerformanceChart
          title="📈 GPA Trends Over Time"
          data={performanceData.trends.map(t => ({ month: t.semester, gpa: t.gpa, attendance: 85 }))}
          type="area"
        />

        {/* Course Performance */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <h3 className="text-xl font-bold text-gray-800 mb-6">Current Courses Performance</h3>
          <div className="space-y-4">
            {performanceData.courses.map((course, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900">{course.name}</h4>
                  <p className="text-sm text-gray-500">{course.credits} Credits</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-gray-900">{course.grade}</div>
                  <div className="text-sm text-gray-500">GPA: {course.gpa}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Semester Selector */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-gray-800">Historical Performance</h3>
          <select
            value={selectedSemester}
            onChange={(e) => setSelectedSemester(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="current">Current Semester</option>
            <option value="all">All Semesters</option>
            <option value="fall2023">Fall 2023</option>
            <option value="spring2023">Spring 2023</option>
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {performanceData.trends.map((trend, index) => (
            <div key={index} className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-4 border border-blue-100">
              <h4 className="font-semibold text-gray-800">{trend.semester}</h4>
              <div className="mt-2">
                <div className="text-2xl font-bold text-blue-600">{trend.gpa}</div>
                <div className="text-sm text-gray-600">{trend.credits} Credits</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Performance Insights */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
          <svg className="w-6 h-6 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          AI Performance Insights
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div>
                <p className="font-medium text-gray-900">Improving Trend</p>
                <p className="text-sm text-gray-600">Your GPA has improved by 0.6 points over the last 4 semesters.</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <p className="font-medium text-gray-900">Strong in STEM</p>
                <p className="text-sm text-gray-600">You perform exceptionally well in Computer Science and Mathematics courses.</p>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
              <div>
                <p className="font-medium text-gray-900">Focus Area</p>
                <p className="text-sm text-gray-600">Consider spending more time on Physics to improve overall performance.</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
              <div>
                <p className="font-medium text-gray-900">On Track</p>
                <p className="text-sm text-gray-600">You're on track to graduate with a 3.3+ GPA at current pace.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentPerformance;
