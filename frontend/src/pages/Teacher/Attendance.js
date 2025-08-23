import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { attendanceAPI, coursesAPI } from '../../services/api';
import toast from 'react-hot-toast';

const TeacherAttendance = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [students, setStudents] = useState([]);
  const [attendanceDate, setAttendanceDate] = useState(new Date().toISOString().split('T')[0]);
  const [attendanceRecords, setAttendanceRecords] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchCourses();
  }, [user]);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      setError(null);
      const teacherCourses = await coursesAPI.getCourses({ teacher_id: user.id });
      setCourses(teacherCourses);
      if (teacherCourses.length > 0) {
        setSelectedCourse(teacherCourses[0]);
        await fetchCourseStudents(teacherCourses[0].id);
      }
    } catch (err) {
      console.error('Error fetching courses:', err);
      setError('Failed to load courses');
      toast.error('Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  const fetchCourseStudents = async (courseId) => {
    try {
      const courseStudents = await coursesAPI.getCourseStudents(courseId);
      setStudents(courseStudents);
      
      // Initialize attendance records
      const initialRecords = {};
      courseStudents.forEach(student => {
        initialRecords[student.id] = {
          status: 'present',
          notes: ''
        };
      });
      setAttendanceRecords(initialRecords);

      // Check if attendance already exists for this date
      await checkExistingAttendance(courseId, attendanceDate);
    } catch (err) {
      console.error('Error fetching students:', err);
      toast.error('Failed to load students');
    }
  };

  const checkExistingAttendance = async (courseId, date) => {
    try {
      const existingAttendance = await attendanceAPI.getAttendance({
        course_id: courseId,
        date_from: date,
        date_to: date
      });

      if (existingAttendance.length > 0) {
        const existingRecords = {};
        existingAttendance.forEach(record => {
          existingRecords[record.student_id] = {
            status: record.status,
            notes: record.notes || ''
          };
        });
        setAttendanceRecords(prev => ({ ...prev, ...existingRecords }));
      }
    } catch (err) {
      console.error('Error checking existing attendance:', err);
    }
  };

  const handleCourseChange = async (course) => {
    setSelectedCourse(course);
    await fetchCourseStudents(course.id);
  };

  const handleDateChange = async (date) => {
    setAttendanceDate(date);
    if (selectedCourse) {
      await checkExistingAttendance(selectedCourse.id, date);
    }
  };

  const updateAttendance = (studentId, field, value) => {
    setAttendanceRecords(prev => ({
      ...prev,
      [studentId]: {
        ...prev[studentId],
        [field]: value
      }
    }));
  };

  const handleSubmitAttendance = async () => {
    if (!selectedCourse) return;

    try {
      setSaving(true);
      
      const attendanceData = Object.entries(attendanceRecords).map(([studentId, record]) => ({
        student_id: studentId,
        status: record.status,
        notes: record.notes
      }));

      await attendanceAPI.createBulkAttendance({
        course_id: selectedCourse.id,
        date: attendanceDate,
        attendance_records: attendanceData
      });

      toast.success('Attendance saved successfully');
    } catch (err) {
      console.error('Error saving attendance:', err);
      toast.error('Failed to save attendance');
    } finally {
      setSaving(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'present': return 'bg-green-100 text-green-800 border-green-200';
      case 'absent': return 'bg-red-100 text-red-800 border-red-200';
      case 'late': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'excused': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getAttendanceStats = () => {
    const total = students.length;
    const present = Object.values(attendanceRecords).filter(r => r.status === 'present').length;
    const absent = Object.values(attendanceRecords).filter(r => r.status === 'absent').length;
    const late = Object.values(attendanceRecords).filter(r => r.status === 'late').length;
    const excused = Object.values(attendanceRecords).filter(r => r.status === 'excused').length;

    return { total, present, absent, late, excused };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading attendance...</p>
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
            onClick={fetchCourses}
            className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Reload Attendance
          </button>
        </div>
      </div>
    );
  }

  const stats = getAttendanceStats();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">📅 Attendance Management</h1>
        <p className="text-green-100 text-lg">
          Track and manage student attendance for your classes
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Select Course</label>
            <select
              value={selectedCourse?.id || ''}
              onChange={(e) => {
                const course = courses.find(c => c.id === e.target.value);
                if (course) handleCourseChange(course);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {courses.map(course => (
                <option key={course.id} value={course.id}>
                  {course.name} ({course.code})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
            <input
              type="date"
              value={attendanceDate}
              onChange={(e) => handleDateChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={handleSubmitAttendance}
              disabled={saving || !selectedCourse}
              className="w-full bg-gradient-to-r from-green-500 to-green-600 text-white px-4 py-2 rounded-lg font-medium hover:from-green-600 hover:to-green-700 transition-all duration-200 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Attendance'}
            </button>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-blue-900">{stats.total}</div>
            <div className="text-sm text-blue-700">Total</div>
          </div>
          <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-green-900">{stats.present}</div>
            <div className="text-sm text-green-700">Present</div>
          </div>
          <div className="bg-gradient-to-r from-red-50 to-red-100 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-red-900">{stats.absent}</div>
            <div className="text-sm text-red-700">Absent</div>
          </div>
          <div className="bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-yellow-900">{stats.late}</div>
            <div className="text-sm text-yellow-700">Late</div>
          </div>
          <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-purple-900">{stats.excused}</div>
            <div className="text-sm text-purple-700">Excused</div>
          </div>
        </div>
      </div>

      {/* Student List */}
      {selectedCourse && students.length > 0 && (
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <h2 className="text-xl font-bold text-gray-800 mb-6">
            {selectedCourse.name} - {new Date(attendanceDate).toLocaleDateString()}
          </h2>

          <div className="space-y-4">
            {students.map((student) => (
              <div key={student.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                    {student.name?.split(' ').map(n => n[0]).join('') || 'S'}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{student.name}</div>
                    <div className="text-sm text-gray-500">{student.email}</div>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="flex space-x-2">
                    {['present', 'absent', 'late', 'excused'].map((status) => (
                      <button
                        key={status}
                        onClick={() => updateAttendance(student.id, 'status', status)}
                        className={`px-3 py-1 rounded-full text-sm font-medium border-2 transition-all duration-200 ${
                          attendanceRecords[student.id]?.status === status
                            ? getStatusColor(status)
                            : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                        }`}
                      >
                        {status.charAt(0).toUpperCase() + status.slice(1)}
                      </button>
                    ))}
                  </div>

                  <input
                    type="text"
                    placeholder="Notes..."
                    value={attendanceRecords[student.id]?.notes || ''}
                    onChange={(e) => updateAttendance(student.id, 'notes', e.target.value)}
                    className="w-32 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-green-500"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedCourse && students.length === 0 && (
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-12 shadow-xl border border-white/20 text-center">
          <div className="text-gray-400 text-6xl mb-4">👥</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">No Students Enrolled</h2>
          <p className="text-gray-600">This course doesn't have any students enrolled yet.</p>
        </div>
      )}
    </div>
  );
};

export default TeacherAttendance;
