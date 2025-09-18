import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { coursesAPI } from '../../services/api';
import toast from 'react-hot-toast';

const TeacherClasses = () => {
  const { user } = useAuth();
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedClass, setSelectedClass] = useState(null);

  useEffect(() => {
    fetchClasses();
  }, [user]);

  const fetchClasses = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch teacher's courses
      const teacherCourses = await coursesAPI.getCourses({ teacher_id: user.id });

      // Process courses data
      const processedClasses = await Promise.all(
        teacherCourses.map(async (course) => {
          try {
            // Fetch students for each course
            const students = await coursesAPI.getCourseStudents(course.id);

            return {
              id: course.id,
              name: course.name,
              code: course.code,
              semester: course.semester,
              students: course.student_count || students.length,
              schedule: course.schedule || 'TBD',
              room: course.room || 'TBD',
              status: course.is_active ? 'active' : 'inactive',
              studentList: students.map(student => ({
                id: student.id,
                name: student.name,
                email: student.email,
                attendance: student.attendance || 0,
                gpa: student.gpa || 0,
                riskLevel: student.risk_level || 'low'
              }))
            };
          } catch (err) {
            console.error(`Error fetching students for course ${course.id}:`, err);
            return {
              id: course.id,
              name: course.name,
              code: course.code,
              semester: course.semester,
              students: course.student_count || 0,
              schedule: course.schedule || 'TBD',
              room: course.room || 'TBD',
              status: course.is_active ? 'active' : 'inactive',
              studentList: []
            };
          }
        })
      );

      setClasses(processedClasses);
    } catch (err) {
      console.error('Error fetching classes:', err);
      setError('Failed to load your classes. Please try again.');
      toast.error('Failed to load classes');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getAttendanceColor = (attendance) => {
    if (attendance >= 90) return 'text-green-600';
    if (attendance >= 75) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your classes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">👥</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Classes Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchClasses}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Reload Classes
          </button>
        </div>
      </div>
    );
  }

  if (!classes || classes.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-gray-400 text-6xl mb-4">🎓</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">No Classes Assigned</h2>
          <p className="text-gray-600">You don't have any classes assigned yet. Contact your administrator.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">👥 My Classes</h1>
        <p className="text-blue-100 text-lg">
          Manage your classes and monitor student progress
        </p>
      </div>

      {/* Classes Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {classes.map((classItem) => (
          <div key={classItem.id} className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20 hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-800">{classItem.name}</h3>
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                {classItem.code}
              </span>
            </div>

            <div className="space-y-3 mb-6">
              <div className="flex items-center text-gray-600">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
                {classItem.students} Students
              </div>
              <div className="flex items-center text-gray-600">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {classItem.schedule}
              </div>
              <div className="flex items-center text-gray-600">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {classItem.room}
              </div>
            </div>

            <div className="flex space-x-2">
              <button
                onClick={() => setSelectedClass(classItem)}
                className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200"
              >
                View Students
              </button>
           
            </div>
          </div>
        ))}
      </div>

      {/* Student List Modal/Detail View */}
      {selectedClass && (
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800">
              {selectedClass.name} - Student List
            </h2>
            <button
              onClick={() => setSelectedClass(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="bg-gradient-to-r from-gray-50 to-gray-100">
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Student
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Attendance
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    GPA
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Risk Level
                  </th>
              
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {selectedClass.studentList.map((student) => (
                  <tr key={student.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                          {student.name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{student.name}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {student.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${getAttendanceColor(student.attendance)}`}>
                        {student.attendance}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {student.gpa}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getRiskColor(student.riskLevel)}`}>
                        {student.riskLevel}
                      </span>
                    </td>
                  
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    

      {/* Class Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Total Students</h3>
          <div className="text-3xl font-bold text-blue-600">
            {classes.reduce((sum, cls) => sum + cls.students, 0)}
          </div>
          <p className="text-sm text-gray-600 mt-2">Across all classes</p>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Active Classes</h3>
          <div className="text-3xl font-bold text-green-600">{classes.length}</div>
          <p className="text-sm text-gray-600 mt-2">This semester</p>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Average Class Size</h3>
          <div className="text-3xl font-bold text-purple-600">
            {Math.round(classes.reduce((sum, cls) => sum + cls.students, 0) / classes.length)}
          </div>
          <p className="text-sm text-gray-600 mt-2">Students per class</p>
        </div>
      </div>
    </div>
  );
};

export default TeacherClasses;
