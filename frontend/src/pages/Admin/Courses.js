import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { coursesAPI, usersAPI } from '../../services/api';
import toast from 'react-hot-toast';

const AdminCourses = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSemester, setFilterSemester] = useState('all');
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: '',
    department: '',
    teacher_id: '',
    semester: 'Fall 2024',
    academic_year: '2024',
    credits: 3,
    max_students: 30,
    schedule: '',
    room: ''
  });

  // Enrollment states
  const [showEnrollModal, setShowEnrollModal] = useState(false);
  const [enrolledStudents, setEnrolledStudents] = useState([]);
  const [allStudents, setAllStudents] = useState([]);
  const [selectedEnrollCourse, setSelectedEnrollCourse] = useState(null);
  const [selectedStudentId, setSelectedStudentId] = useState('');

  useEffect(() => {
    fetchCourses();
    fetchTeachers();
  }, [filterSemester]);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {};
      if (filterSemester !== 'all') params.semester = filterSemester;

      const fetchedCourses = await coursesAPI.getCourses(params);
      setCourses(fetchedCourses);
    } catch (err) {
      console.error('Error fetching courses:', err);
      setError('Failed to load courses. Please try again.');
      toast.error('Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  const fetchTeachers = async () => {
    try {
      const fetchedTeachers = await usersAPI.getUsers({ role: 'teacher' });
      setTeachers(fetchedTeachers);
    } catch (err) {
      console.error('Error fetching teachers:', err);
      toast.error('Failed to load teachers');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Validate required fields
      if (!formData.name || !formData.code || !formData.teacher_id) {
        toast.error('Please fill in all required fields');
        return;
      }

      if (selectedCourse) {
        await coursesAPI.updateCourse(selectedCourse.id, formData);
        toast.success('Course updated successfully');
      } else {
        await coursesAPI.createCourse(formData);
        toast.success('Course created successfully');
      }
      setShowModal(false);
      setSelectedCourse(null);
      resetForm();
      fetchCourses();
    } catch (err) {
      console.error('Error saving course:', err);
      toast.error(selectedCourse ? 'Failed to update course' : 'Failed to create course');
    }
  };

  const handleEditCourse = (course) => {
    setSelectedCourse(course);
    setFormData({
      name: course.name || '',
      code: course.code || '',
      description: course.description || '',
      department: course.department || '',
      teacher_id: course.teacher_id || '',
      semester: course.semester || 'Fall 2024',
      academic_year: course.academic_year || '2024',
      credits: course.credits || 3,
      max_students: course.max_students || 30,
      schedule: course.schedule || '',
      room: course.room || ''
    });
    setShowModal(true);
  };

  const handleDeleteCourse = async (courseId) => {
    if (window.confirm('Are you sure you want to delete this course?')) {
      try {
        await coursesAPI.deleteCourse(courseId);
        toast.success('Course deleted successfully');
        fetchCourses();
      } catch (err) {
        console.error('Error deleting course:', err);
        toast.error('Failed to delete course');
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      code: '',
      description: '',
      department: '',
      teacher_id: '',
      semester: 'Fall 2024',
      academic_year: '2024',
      credits: 3,
      max_students: 30,
      schedule: '',
      room: ''
    });
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const filteredCourses = courses.filter(course =>
    course.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    course.code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    course.teacher_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (isActive) => (isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800');

  // Enrollment handlers
  const handleOpenEnrollModal = async (course) => {
    setSelectedEnrollCourse(course);
    try {
      const students = await coursesAPI.getCourseStudents(course.id);
      setEnrolledStudents(students);

      const allStudentUsers = await usersAPI.getUsers({ role: 'student' });
      setAllStudents(allStudentUsers);
    } catch (err) {
      console.error('Error loading students:', err);
      toast.error('Failed to load students');
    }
    setShowEnrollModal(true);
  };

  const handleEnrollStudent = async () => {
    if (!selectedStudentId) {
      toast.error('Please select a student');
      return;
    }
    try {
      await coursesAPI.enrollStudent(selectedEnrollCourse.id, selectedStudentId);
      toast.success('Student enrolled successfully');
      const students = await coursesAPI.getCourseStudents(selectedEnrollCourse.id);
      console.log(students)
      setEnrolledStudents(students);
      setSelectedStudentId('');
      fetchCourses(); // Refresh courses list
    } catch (err) {
      console.error('Error enrolling student:', err);
      toast.error('Failed to enroll student');
    }
  };

  const handleUnenrollStudent = async (studentId) => {
    try {
      await coursesAPI.unenrollStudent(selectedEnrollCourse.id, studentId);
      toast.success('Student unenrolled successfully');
      const students = await coursesAPI.getCourseStudents(selectedEnrollCourse.id);
      setEnrolledStudents(students);
      fetchCourses(); // Refresh courses list
    } catch (err) {
      console.error('Error unenrolling student:', err);
      toast.error('Failed to unenroll student');
    }
  };

  if (loading) return <div className="flex items-center justify-center h-64">Loading...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-600 to-pink-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">📚 Course Management</h1>
        <p className="text-red-100 text-lg">Manage courses, teachers, and students</p>
      </div>

      {/* Controls */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <input
              type="text"
              placeholder="Search courses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-3 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
            />
            <select
              value={filterSemester}
              onChange={(e) => setFilterSemester(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <option value="all">All Semesters</option>
              <option value="Fall 2024">Fall 2024</option>
              <option value="Spring 2024">Spring 2024</option>
              <option value="Summer 2024">Summer 2024</option>
            </select>
          </div>
          <button
            onClick={() => { setSelectedCourse(null); resetForm(); setShowModal(true); }}
            className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:from-blue-600 hover:to-blue-700"
          >
            Add New Course
          </button>
        </div>
      </div>

      {/* Courses Table */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Course</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Teacher</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Semester</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Students</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredCourses.map(course => (
                <tr key={course.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{course.name}</div>
                    <div className="text-sm text-gray-500">{course.code}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {course.teacher_name || 'Unassigned'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{course.semester}</div>
                    <div className="text-sm text-gray-500">{course.academic_year}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {course.student_count || 0} / {course.max_students || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(course.is_active)}`}>
                      {course.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button 
                      onClick={() => handleOpenEnrollModal(course)} 
                      className="text-purple-600 hover:text-purple-900 mr-4"
                    >
                      Students
                    </button>
                    <button 
                      onClick={() => handleEditCourse(course)} 
                      className="text-blue-600 hover:text-blue-900 mr-4"
                    >
                      Edit
                    </button>
                    <button 
                      onClick={() => handleDeleteCourse(course.id)} 
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Course Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">{selectedCourse ? 'Edit Course' : 'Add New Course'}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Course Name *</label>
                  <input 
                    type="text" 
                    name="name" 
                    placeholder="Course Name" 
                    value={formData.name} 
                    onChange={handleInputChange} 
                    required 
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" 
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Course Code *</label>
                  <input 
                    type="text" 
                    name="code" 
                    placeholder="Course Code" 
                    value={formData.code} 
                    onChange={handleInputChange} 
                    required 
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" 
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea 
                  name="description" 
                  placeholder="Course Description" 
                  value={formData.description} 
                  onChange={handleInputChange} 
                  rows="3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" 
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                <input 
                  type="text" 
                  name="department" 
                  placeholder="Department" 
                  value={formData.department} 
                  onChange={handleInputChange} 
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" 
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Teacher *</label>
                <select 
                  name="teacher_id" 
                  value={formData.teacher_id} 
                  onChange={handleInputChange} 
                  required 
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Teacher</option>
                  {teachers.map(t => (
                    <option key={t.id} value={t.id}>
                      {t.first_name} {t.last_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Semester</label>
                  <select 
                    name="semester" 
                    value={formData.semester} 
                    onChange={handleInputChange} 
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Fall 2024">Fall 2024</option>
                    <option value="Spring 2024">Spring 2024</option>
                    <option value="Summer 2024">Summer 2024</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Academic Year</label>
                  <input 
                    type="text" 
                    name="academic_year" 
                    value={formData.academic_year} 
                    onChange={handleInputChange} 
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" 
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Credits</label>
                  <input 
                    type="number" 
                    name="credits" 
                    value={formData.credits} 
                    onChange={handleInputChange} 
                    min="1" 
                    max="6" 
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" 
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max Students</label>
                  <input 
                    type="number" 
                    name="max_students" 
                    value={formData.max_students} 
                    onChange={handleInputChange} 
                    min="1" 
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" 
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Schedule</label>
                  <input 
                    type="text" 
                    name="schedule" 
                    value={formData.schedule} 
                    onChange={handleInputChange} 
                    placeholder="e.g., MWF 10:00-11:00" 
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" 
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Room</label>
                  <input 
                    type="text" 
                    name="room" 
                    value={formData.room} 
                    onChange={handleInputChange} 
                    placeholder="Room Number" 
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" 
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-6">
                <button 
                  type="button" 
                  onClick={() => { setShowModal(false); resetForm(); }} 
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
                >
                  {selectedCourse ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Enrollment Modal */}
      {showEnrollModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">Manage Students for {selectedEnrollCourse?.name}</h2>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Enroll New Student</label>
              <div className="flex gap-2">
                <select 
                  value={selectedStudentId} 
                  onChange={(e) => setSelectedStudentId(e.target.value)} 
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Student to Enroll</option>
                  {allStudents.filter(s => !enrolledStudents.some(e => e.student_id === s.id)).map(s => (
                    <option key={s.student_id} value={s.student_id}>
                      {s.first_name} {s.last_name}
                    </option>

                  ))}
                </select>
                <button 
                  onClick={handleEnrollStudent} 
                  disabled={!selectedStudentId}
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50"
                >
                  Enroll
                </button>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">Enrolled Students ({enrolledStudents.length})</h3>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {enrolledStudents.map(s => (
                  <div key={s.student_id} className="flex justify-between items-center p-3 border border-gray-200 rounded-lg">
                    <div>
                      <div className="font-medium text-gray-900">{s.name}</div>
                      <div className="text-sm text-gray-500">{s.email}</div>
                    </div>
                    <button 
                      onClick={() => handleUnenrollStudent(s.student_id)} 
                      className="px-3 py-1 bg-red-500 text-white rounded-lg text-sm hover:bg-red-600"
                    >
                      Unenroll
                    </button>
                  </div>
                ))}
                {enrolledStudents.length === 0 && (
                  <p className="text-gray-500 text-center py-4">No students enrolled</p>
                )}
              </div>
            </div>

            <div className="flex justify-end mt-6">
              <button 
                onClick={() => setShowEnrollModal(false)} 
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminCourses;