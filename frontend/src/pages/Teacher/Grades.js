import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { gradesAPI, coursesAPI } from '../../services/api';
import toast from 'react-hot-toast';

const TeacherGrades = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [gradebook, setGradebook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showGradeModal, setShowGradeModal] = useState(false);
  const [gradeForm, setGradeForm] = useState({
    assignment_name: '',
    grade_type: 'assignment',
    points_possible: 100,
    due_date: '',
    grades: []
  });

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
        await fetchGradebook(teacherCourses[0].id);
      }
    } catch (err) {
      console.error('Error fetching courses:', err);
      setError('Failed to load courses');
      toast.error('Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  const fetchGradebook = async (courseId) => {
    try {
      const gradebookData = await gradesAPI.getCourseGradebook(courseId);
      setGradebook(gradebookData);
    } catch (err) {
      console.error('Error fetching gradebook:', err);
      toast.error('Failed to load gradebook');
    }
  };

  const handleCourseChange = async (course) => {
    setSelectedCourse(course);
    await fetchGradebook(course.id);
  };

  const handleAddAssignment = () => {
    if (!selectedCourse) return;
    
    // Initialize grades for all students
    const studentGrades = gradebook?.students?.map(student => ({
      student_id: student.student_id,
      points_earned: 0,
      notes: ''
    })) || [];

    setGradeForm({
      assignment_name: '',
      grade_type: 'assignment',
      points_possible: 100,
      due_date: '',
      grades: studentGrades
    });
    setShowGradeModal(true);
  };

  const handleGradeSubmit = async (e) => {
    e.preventDefault();
    try {
      await gradesAPI.createBulkGrades({
        course_id: selectedCourse.id,
        assignment_name: gradeForm.assignment_name,
        grade_type: gradeForm.grade_type,
        points_possible: gradeForm.points_possible,
        due_date: gradeForm.due_date || null,
        grades: gradeForm.grades
      });

      toast.success('Grades added successfully');
      setShowGradeModal(false);
      await fetchGradebook(selectedCourse.id);
    } catch (err) {
      console.error('Error adding grades:', err);
      toast.error('Failed to add grades');
    }
  };

  const updateGradeForm = (field, value) => {
    setGradeForm(prev => ({ ...prev, [field]: value }));
  };

  const updateStudentGrade = (studentId, field, value) => {
    setGradeForm(prev => ({
      ...prev,
      grades: prev.grades.map(grade =>
        grade.student_id === studentId
          ? { ...grade, [field]: value }
          : grade
      )
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading gradebook...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">📊</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Gradebook Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchCourses}
            className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Reload Gradebook
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">📊 Grade Management</h1>
        <p className="text-green-100 text-lg">
          Manage grades and track student performance
        </p>
      </div>

      {/* Course Selection */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-800">Select Course</h2>
          <button
            onClick={handleAddAssignment}
            disabled={!selectedCourse}
            className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200 disabled:opacity-50"
          >
            Add Assignment
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {courses.map((course) => (
            <button
              key={course.id}
              onClick={() => handleCourseChange(course)}
              className={`p-4 rounded-xl border-2 transition-all duration-200 text-left ${
                selectedCourse?.id === course.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <h3 className="font-semibold text-gray-800">{course.name}</h3>
              <p className="text-sm text-gray-600">{course.code}</p>
              <p className="text-xs text-gray-500">{course.student_count} students</p>
            </button>
          ))}
        </div>
      </div>

      {/* Gradebook */}
      {selectedCourse && gradebook && (
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
          <h2 className="text-xl font-bold text-gray-800 mb-6">
            {selectedCourse.name} - Gradebook
          </h2>

          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="bg-gradient-to-r from-gray-50 to-gray-100">
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Student
                  </th>
                  {gradebook.assignments?.map((assignment, index) => (
                    <th key={index} className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      <div>{assignment.name}</div>
                      <div className="text-xs text-gray-400">({assignment.points_possible} pts)</div>
                    </th>
                  ))}
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Current Grade
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {gradebook.students?.map((student) => (
                  <tr key={student.student_id} className="hover:bg-gray-50">
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                          {student.student_name?.split(' ').map(n => n[0]).join('') || 'S'}
                        </div>
                        <div className="ml-3">
                          <div className="text-sm font-medium text-gray-900">{student.student_name}</div>
                        </div>
                      </div>
                    </td>
                    {gradebook.assignments?.map((assignment, index) => {
                      const assignmentKey = `${assignment.name}_${assignment.type}`;
                      const grade = student.grades?.[assignmentKey];
                      return (
                        <td key={index} className="px-4 py-4 text-center">
                          {grade ? (
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {grade.points_earned}/{assignment.points_possible}
                              </div>
                              <div className="text-xs text-gray-500">
                                {grade.percentage}%
                              </div>
                            </div>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                      );
                    })}
                    <td className="px-4 py-4 text-center">
                      <div className="text-sm font-medium text-gray-900">
                        {student.current_grade || 'N/A'}
                      </div>
                      <div className="text-xs text-gray-500">
                        {student.current_percentage ? `${student.current_percentage}%` : ''}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Class Statistics */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl p-4">
              <h3 className="text-sm font-medium text-blue-800">Class Average</h3>
              <p className="text-2xl font-bold text-blue-900">
                {gradebook.statistics?.class_average || 'N/A'}%
              </p>
            </div>
            <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-xl p-4">
              <h3 className="text-sm font-medium text-green-800">Total Students</h3>
              <p className="text-2xl font-bold text-green-900">
                {gradebook.statistics?.total_students || 0}
              </p>
            </div>
            <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-xl p-4">
              <h3 className="text-sm font-medium text-purple-800">Assignments</h3>
              <p className="text-2xl font-bold text-purple-900">
                {gradebook.statistics?.total_assignments || 0}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Add Assignment Modal */}
      {showGradeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Add New Assignment</h2>
            
            <form onSubmit={handleGradeSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Assignment Name</label>
                  <input
                    type="text"
                    value={gradeForm.assignment_name}
                    onChange={(e) => updateGradeForm('assignment_name', e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                  <select
                    value={gradeForm.grade_type}
                    onChange={(e) => updateGradeForm('grade_type', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="assignment">Assignment</option>
                    <option value="quiz">Quiz</option>
                    <option value="exam">Exam</option>
                    <option value="project">Project</option>
                    <option value="participation">Participation</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Points Possible</label>
                  <input
                    type="number"
                    value={gradeForm.points_possible}
                    onChange={(e) => updateGradeForm('points_possible', parseInt(e.target.value))}
                    required
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Due Date (Optional)</label>
                  <input
                    type="date"
                    value={gradeForm.due_date}
                    onChange={(e) => updateGradeForm('due_date', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Student Grades */}
              <div>
                <h3 className="text-lg font-medium text-gray-800 mb-4">Student Grades</h3>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {gradeForm.grades.map((grade, index) => {
                    const student = gradebook?.students?.find(s => s.student_id === grade.student_id);
                    return (
                      <div key={grade.student_id} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <span className="text-sm font-medium text-gray-900">
                            {student?.student_name || `Student ${index + 1}`}
                          </span>
                        </div>
                        <div className="w-24">
                          <input
                            type="number"
                            placeholder="Points"
                            value={grade.points_earned}
                            onChange={(e) => updateStudentGrade(grade.student_id, 'points_earned', parseFloat(e.target.value) || 0)}
                            min="0"
                            max={gradeForm.points_possible}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                          />
                        </div>
                        <div className="w-32">
                          <input
                            type="text"
                            placeholder="Notes"
                            value={grade.notes}
                            onChange={(e) => updateStudentGrade(grade.student_id, 'notes', e.target.value)}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="flex justify-end space-x-4">
                <button
                  type="button"
                  onClick={() => setShowGradeModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700"
                >
                  Add Assignment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeacherGrades;
