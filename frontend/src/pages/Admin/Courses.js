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
    teacher_id: '',
    semester: 'Fall 2024',
    academic_year: '2024',
    credits: 3,
    max_students: 30,
    schedule: '',
    room: ''
  });

  // --- ENROLLMENT STATES ---
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
      if (selectedCourse) {
        await coursesAPI.updateCourse(selectedCourse._id, formData);
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

  // --- ENROLLMENT HANDLERS ---
  const handleOpenEnrollModal = async (course) => {
    setSelectedEnrollCourse(course);
    try {
      const students = await coursesAPI.getCourseStudents(course._id);
      setEnrolledStudents(students);

      const allUsers = await usersAPI.getUsers({ role: 'student' });
      setAllStudents(allUsers);
    } catch (err) {
      toast.error('Failed to load students');
    }
    setShowEnrollModal(true);
  };

  const handleEnrollStudent = async () => {
    if (!selectedStudentId) return;
    try {
      await coursesAPI.enrollStudent(selectedEnrollCourse._id, selectedStudentId);
      toast.success('Student enrolled successfully');
      const students = await coursesAPI.getCourseStudents(selectedEnrollCourse._id);
      setEnrolledStudents(students);
    } catch (err) {
      toast.error('Failed to enroll student');
    }
  };

  const handleUnenrollStudent = async (studentId) => {
    try {
      await coursesAPI.unenrollStudent(selectedEnrollCourse._id, studentId);
      toast.success('Student unenrolled successfully');
      const students = await coursesAPI.getCourseStudents(selectedEnrollCourse._id);
      setEnrolledStudents(students);
    } catch (err) {
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
                <th>Course</th>
                <th>Teacher</th>
                <th>Semester</th>
                <th>Students</th>
                <th>Status</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredCourses.map(course => (
                <tr key={course._id} className="hover:bg-gray-50">
                  <td>{course.name} <div className="text-gray-500">{course.code}</div></td>
                  <td>{course.teacher_name || 'Unassigned'}</td>
                  <td>{course.semester} <div className="text-gray-500">{course.academic_year}</div></td>
                  <td>{course.student_count || 0} / {course.max_students || 'N/A'}</td>
                  <td>
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(course.is_active)}`}>
                      {course.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="text-right">
                    <button onClick={() => handleOpenEnrollModal(course)} className="text-purple-600 mr-4">Students</button>
                    <button onClick={() => handleEditCourse(course)} className="text-blue-600 mr-4">Edit</button>
                    <button onClick={() => handleDeleteCourse(course._id)} className="text-red-600">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* COURSE CREATE/EDIT MODAL */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">{selectedCourse ? 'Edit Course' : 'Add New Course'}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <input type="text" name="name" placeholder="Course Name" value={formData.name} onChange={handleInputChange} required className="w-full px-3 py-2 border rounded-lg" />
              <input type="text" name="code" placeholder="Course Code" value={formData.code} onChange={handleInputChange} required className="w-full px-3 py-2 border rounded-lg" />
              <textarea name="description" placeholder="Description" value={formData.description} onChange={handleInputChange} className="w-full px-3 py-2 border rounded-lg" />
              <select name="teacher_id" value={formData.teacher_id} onChange={handleInputChange} required className="w-full px-3 py-2 border rounded-lg">
                <option value="">Select Teacher</option>
                {teachers.map(t => <option key={t.id} value={t.id}>{t.first_name} {t.last_name}</option>)}
              </select>
              <div className="flex gap-2">
                <input type="number" name="credits" value={formData.credits} onChange={handleInputChange} min="1" max="6" className="w-1/2 px-3 py-2 border rounded-lg" />
                <input type="number" name="max_students" value={formData.max_students} onChange={handleInputChange} min="1" className="w-1/2 px-3 py-2 border rounded-lg" />
              </div>
              <input type="text" name="schedule" value={formData.schedule} onChange={handleInputChange} placeholder="Schedule" className="w-full px-3 py-2 border rounded-lg" />
              <input type="text" name="room" value={formData.room} onChange={handleInputChange} placeholder="Room" className="w-full px-3 py-2 border rounded-lg" />
              <div className="flex justify-end gap-2 mt-4">
                <button type="button" onClick={() => { setShowModal(false); resetForm(); }} className="px-4 py-2 border rounded-lg">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-red-500 text-white rounded-lg">{selectedCourse ? 'Update' : 'Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ENROLLMENT MODAL */}
      {showEnrollModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">Manage Students for {selectedEnrollCourse.name}</h2>

            <div className="mb-4">
              <select value={selectedStudentId} onChange={(e) => setSelectedStudentId(e.target.value)} className="w-full px-3 py-2 border rounded-lg mb-2">
                <option value="">Select Student to Enroll</option>
                {allStudents.filter(s => !enrolledStudents.some(e => e.id === s.id)).map(s => (
                  <option key={s.id} value={s.id}>{s.first_name} {s.last_name}</option>
                ))}
              </select>
              <button onClick={handleEnrollStudent} className="px-4 py-2 bg-green-500 text-white rounded-lg">Enroll Student</button>
            </div>

            <h3 className="text-lg font-semibold mb-2">Enrolled Students</h3>
            <ul className="space-y-2 max-h-60 overflow-y-auto">
              {enrolledStudents.map(s => (
                <li key={s.id} className="flex justify-between items-center p-2 border rounded-lg">
                  <span>{s.first_name} {s.last_name}</span>
                  <button onClick={() => handleUnenrollStudent(s.id)} className="px-2 py-1 bg-red-500 text-white rounded-lg text-sm">Unenroll</button>
                </li>
              ))}
            </ul>

            <div className="flex justify-end mt-4">
              <button onClick={() => setShowEnrollModal(false)} className="px-4 py-2 border rounded-lg">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminCourses;
