import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { coursesAPI } from '../../services/api';
import toast from 'react-hot-toast';

const StudentCourses = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user?.id) {
      fetchCourses();
    }
  }, [user]);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      setError(null);

      // ✅ Pass the actual student ID instead of "me"
      const studentCourses = await coursesAPI.getCourses({ student_id: user.id });
      setCourses(studentCourses);

    } catch (err) {
      console.error('Error fetching courses:', err);
      setError('Failed to load courses. Please try again.');
      toast.error('Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your courses...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">📚</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Courses Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchCourses}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Reload Courses
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">📚 My Courses</h1>
        <p className="text-blue-100 text-lg">
          View your enrolled courses and academic progress
        </p>
      </div>

      {/* Courses Grid */}
      {courses.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <div key={course.id} className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-800">{course.name}</h3>
                  <p className="text-gray-600">{course.code}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${course.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                  {course.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>

              <div className="space-y-3 mb-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Instructor</span>
                  <span className="font-medium text-gray-800">{course.teacher_name || 'TBD'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Credits</span>
                  <span className="font-medium text-gray-800">{course.credits || 3}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Schedule</span>
                  <span className="font-medium text-gray-800">{course.schedule || 'TBD'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Room</span>
                  <span className="font-medium text-gray-800">{course.room || 'TBD'}</span>
                </div>
              </div>

              {course.description && (
                <div className="mb-4">
                  <p className="text-sm text-gray-600">{course.description}</p>
                </div>
              )}

              <div className="flex justify-between items-center pt-4 border-t border-gray-200">
                <div className="text-sm text-gray-500">
                  {course.semester} {course.academic_year}
                </div>
                <div className="text-sm font-medium text-blue-600">
                  Current Grade: {course.current_grade || 'N/A'}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📚</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No courses enrolled</h3>
          <p className="text-gray-500">You are not currently enrolled in any courses.</p>
        </div>
      )}
    </div>
  );
};

export default StudentCourses;
