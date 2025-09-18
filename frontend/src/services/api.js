import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Request interceptor to add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  response => response,
  (error) => {
    const errorDetails = error.response?.data || error.message;
    console.error('API Error:', errorDetails);
    
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken');
      // Only redirect if not already on login page
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    
    // Return a more user-friendly error
    const errorMessage = error.response?.data?.detail || 
                         error.response?.data?.message || 
                         error.message || 
                         'An unexpected error occurred';
    return Promise.reject(new Error(errorMessage));
  }
);

// Helper function to handle API calls with error handling
const handleApiCall = async (apiCall) => {
  try {
    const response = await apiCall();
    return response.data;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

// -------------------- AUTH API --------------------
export const authAPI = {
  login: async (email, password) => {
    return handleApiCall(() => apiClient.post('/auth/login', { email, password }));
  },

  register: async (userData) => {
    return handleApiCall(() => apiClient.post('/auth/register', userData));
  },

  getCurrentUser: async () => {
    return handleApiCall(() => apiClient.get('/auth/me'));
  },

  logout: async () => {
    localStorage.removeItem('accessToken');
  },
};

// -------------------- USERS API --------------------
export const usersAPI = {
  getUsers: async (params = {}) => {
    return handleApiCall(() => apiClient.get('/users/', { params }));
  },
  
  createUser: async (data) => {
    return handleApiCall(() => apiClient.post('/users/', data));
  },
  
  getUserById: async (id) => {
    return handleApiCall(() => apiClient.get(`/users/${id}`));
  },
  
  updateUser: async (id, data) => {
    return handleApiCall(() => apiClient.put(`/users/${id}`, data));
  },
  
  deleteUser: async (id) => {
    return handleApiCall(() => apiClient.delete(`/users/${id}`));
  },
};

// -------------------- STUDENTS API --------------------
export const studentsAPI = {
  getStudents: async (params = {}) => {
    return handleApiCall(() => apiClient.get('/students', { params }));
  },
  
  getStudentById: async (id) => {
    return handleApiCall(() => apiClient.get(`/students/${id}`));
  },
  
  createStudent: async (data) => {
    return handleApiCall(() => apiClient.post('/students', data));
  },
  
  updateStudent: async (id, data) => {
    return handleApiCall(() => apiClient.put(`/students/${id}`, data));
  },
  
  getStudentAnalytics: async (id) => {
    return handleApiCall(() => apiClient.get(`/students/${id}/analytics`));
  },
};

// -------------------- COURSES API --------------------
export const coursesAPI = {
  getCourses: async (params = {}) => {
    return handleApiCall(() => apiClient.get('/courses', { params }));
  },
  
  getCourseById: async (id) => {
    return handleApiCall(() => apiClient.get(`/courses/${id}`));
  },
  
  createCourse: async (data) => {
    return handleApiCall(() => apiClient.post('/courses', data));
  },
  
  updateCourse: async (id, data) => {
    return handleApiCall(() => apiClient.put(`/courses/${id}`, data));
  },
  
  deleteCourse: async (id) => {
    return handleApiCall(() => apiClient.delete(`/courses/${id}`));
  },

  getCourseStudents: async (courseId) => {
    return handleApiCall(() => apiClient.get(`/courses/${courseId}/students`));
  },

  enrollStudent: async (courseId, studentId) => {
    return handleApiCall(() => apiClient.post(`/courses/${courseId}/enroll/${studentId}`));
  },

  unenrollStudent: async (courseId, studentId) => {
    return handleApiCall(() => apiClient.delete(`/courses/${courseId}/enroll/${studentId}`));
  },
};

// -------------------- ATTENDANCE API --------------------
export const attendanceAPI = {
  getAttendance: async (params = {}) => {
    return handleApiCall(() => apiClient.get('/attendance', { params }));
  },
  
  markAttendance: async (data) => {
    return handleApiCall(() => apiClient.post('/attendance', data));
  },
  
  createBulkAttendance: async (data) => {
    return handleApiCall(() => apiClient.post('/attendance/bulk', data));
  },
  
  getAttendanceStats: async (studentId, courseId) => {
    return handleApiCall(() => apiClient.get(`/attendance/${studentId}/${courseId}/stats`));
  },
};

// -------------------- GRADES API --------------------
export const gradesAPI = {
  getGrades: async (params = {}) => {
    return handleApiCall(() => apiClient.get('/grades', { params }));
  },
  
  createGrade: async (data) => {
    return handleApiCall(() => apiClient.post('/grades', data));
  },
  
  createBulkGrades: async (data) => {
    return handleApiCall(() => apiClient.post('/grades/bulk', data));
  },
  
  getCourseGradebook: async (courseId) => {
    return handleApiCall(() => apiClient.get(`/grades/course/${courseId}/gradebook`));
  },
  
  getGradeStats: async (studentId, courseId) => {
    return handleApiCall(() => apiClient.get(`/grades/${studentId}/${courseId}/stats`));
  },
};

// -------------------- ANALYTICS API --------------------
export const analyticsAPI = {
  getDropoutPrediction: async (studentId) => {
    return handleApiCall(() => apiClient.get(`/analytics/dropout-prediction/${studentId}`));
  },

  getGradePredictions: async (studentId) => {
    return handleApiCall(() => apiClient.get(`/analytics/grade-predictions/${studentId}`));
  },

  getPerformanceTrends: async (studentId) => {
    return handleApiCall(() => apiClient.get(`/analytics/performance-trends/${studentId}`));
  },

  getDashboardStats: async (role) => {
    return handleApiCall(() => apiClient.get(`/analytics/dashboard-stats/${role}`));
  },

  getInstitutionAnalytics: async () => {
    return handleApiCall(() => apiClient.get('/analytics/institution-analytics'));
  },

  getAtRiskStudents: async (limit = 20) => {
    return handleApiCall(() => apiClient.get('/analytics/at-risk-students', { params: { limit } }));
  },

  getStudentAnalytics: async (studentId) => {
    return handleApiCall(() => apiClient.get(`/analytics/${studentId}`));
  },

  getClassAnalytics: async (courseId) => {
    // Mock implementation for class analytics
    return {
      grade_distribution: { A: 5, B: 8, C: 4, D: 2, F: 1 },
      performance_trends: [
        { month: 'Jan', gpa: 3.1, attendance: 85 },
        { month: 'Feb', gpa: 3.2, attendance: 87 },
        { month: 'Mar', gpa: 3.1, attendance: 83 }
      ],
      at_risk_students: [
        { name: 'John Doe', gpa: 2.1, attendance_rate: 65, risk_factors: ['Low GPA', 'Poor Attendance'] }
      ],
      total_students: 20
    };
  },
};

// -------------------- NOTIFICATIONS API --------------------
export const notificationsAPI = {
  getNotifications: async (params = {}) => {
    const userId = params.user_id || 'me';
    return handleApiCall(() => apiClient.get(`/notifications/${userId}`));
  },
  
  createNotification: async (data) => {
    return handleApiCall(() => apiClient.post('/notifications', data));
  },
  
  markAsRead: async (id) => {
    return handleApiCall(() => apiClient.put(`/notifications/${id}/read`));
  },
  
  markAllAsRead: async () => {
    return handleApiCall(() => apiClient.put('/notifications/read-all'));
  },
};

export default apiClient;