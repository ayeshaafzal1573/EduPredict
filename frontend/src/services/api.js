import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 10000, // 10 second timeout
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
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// -------------------- AUTH API --------------------
export const authAPI = {
  login: async (email, password) => {
    const response = await apiClient.post('/auth/login', { email, password });
    return response.data;
  },

  register: async (userData) => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  logout: async () => {
    localStorage.removeItem('accessToken');
  },
};

// -------------------- USERS API --------------------
export const usersAPI = {
  getUsers: async (params = {}) => {
    const response = await apiClient.get('/users/', { params });
    return response.data;
  },
  
  createUser: async (data) => {
    const response = await apiClient.post('/users/', data);
    return response.data;
  },
  
  getUserById: async (id) => {
    const response = await apiClient.get(`/users/${id}`);
    return response.data;
  },
  
  updateUser: async (id, data) => {
    const response = await apiClient.put(`/users/${id}`, data);
    return response.data;
  },
  
  deleteUser: async (id) => {
    const response = await apiClient.delete(`/users/${id}`);
    return response.data;
  },
};

// -------------------- STUDENTS API --------------------
export const studentsAPI = {
  getStudents: async (params = {}) => {
    const response = await apiClient.get('/students', { params });
    return response.data;
  },
  
  getStudentById: async (id) => {
    const response = await apiClient.get(`/students/${id}`);
    return response.data;
  },
  
  createStudent: async (data) => {
    const response = await apiClient.post('/students', data);
    return response.data;
  },
  
  updateStudent: async (id, data) => {
    const response = await apiClient.put(`/students/${id}`, data);
    return response.data;
  },
  
  getStudentAnalytics: async (id) => {
    const response = await apiClient.get(`/students/${id}/analytics`);
    return response.data;
  },
};

// -------------------- COURSES API --------------------
export const coursesAPI = {
  getCourses: async (params = {}) => {
    const response = await apiClient.get('/courses', { params });
    return response.data;
  },
  
  getCourseById: async (id) => {
    const response = await apiClient.get(`/courses/${id}`);
    return response.data;
  },
  
  createCourse: async (data) => {
    const response = await apiClient.post('/courses', data);
    return response.data;
  },
  
  updateCourse: async (id, data) => {
    const response = await apiClient.put(`/courses/${id}`, data);
    return response.data;
  },
  
  deleteCourse: async (id) => {
    const response = await apiClient.delete(`/courses/${id}`);
    return response.data;
  },

  getCourseStudents: async (courseId) => {
    const response = await apiClient.get(`/courses/${courseId}/students`);
    return response.data;
  },

  enrollStudent: async (courseId, studentId) => {
    const response = await apiClient.post(`/courses/${courseId}/enroll/${studentId}`);
    return response.data;
  },

  unenrollStudent: async (courseId, studentId) => {
    const response = await apiClient.delete(`/courses/${courseId}/enroll/${studentId}`);
    return response.data;
  },
};

// -------------------- ATTENDANCE API --------------------
export const attendanceAPI = {
  getAttendance: async (params = {}) => {
    const response = await apiClient.get('/attendance', { params });
    return response.data;
  },
  
  markAttendance: async (data) => {
    const response = await apiClient.post('/attendance', data);
    return response.data;
  },
  
  createBulkAttendance: async (data) => {
    const response = await apiClient.post('/attendance/bulk', data);
    return response.data;
  },
  
  getAttendanceStats: async (studentId, courseId) => {
    const response = await apiClient.get(`/attendance/${studentId}/${courseId}/stats`);
    return response.data;
  },
};

// -------------------- GRADES API --------------------
export const gradesAPI = {
  getGrades: async (params = {}) => {
    const response = await apiClient.get('/grades', { params });
    return response.data;
  },
  
  createGrade: async (data) => {
    const response = await apiClient.post('/grades', data);
    return response.data;
  },
  
  createBulkGrades: async (data) => {
    const response = await apiClient.post('/grades/bulk', data);
    return response.data;
  },
  
  getCourseGradebook: async (courseId) => {
    const response = await apiClient.get(`/grades/course/${courseId}/gradebook`);
    return response.data;
  },
  
  getGradeStats: async (studentId, courseId) => {
    const response = await apiClient.get(`/grades/${studentId}/${courseId}/stats`);
    return response.data;
  },
};

// -------------------- ANALYTICS API --------------------
export const analyticsAPI = {
  getDropoutPrediction: async (studentId) => {
    const response = await apiClient.get(`/analytics/dropout-prediction/${studentId}`);
    return response.data;
  },

  getGradePredictions: async (studentId) => {
    const response = await apiClient.get(`/analytics/grade-predictions/${studentId}`);
    return response.data;
  },

  getPerformanceTrends: async (studentId) => {
    const response = await apiClient.get(`/analytics/performance-trends/${studentId}`);
    return response.data;
  },

  getDashboardStats: async (role) => {
    const response = await apiClient.get(`/analytics/dashboard-stats/${role}`);
    return response.data;
  },

  getInstitutionAnalytics: async () => {
    const response = await apiClient.get('/analytics/institution-analytics');
    return response.data;
  },

  getAtRiskStudents: async (limit = 20) => {
    const response = await apiClient.get('/analytics/at-risk-students', { params: { limit } });
    return response.data;
  },

  getStudentAnalytics: async (studentId) => {
    const response = await apiClient.get(`/analytics/${studentId}`);
    return response.data;
  },
};

// -------------------- NOTIFICATIONS API --------------------
export const notificationsAPI = {
  getNotifications: async (params = {}) => {
    const response = await apiClient.get(`/notifications/${params.user_id || 'me'}`);
    return response.data;
  },
  
  createNotification: async (data) => {
    const response = await apiClient.post('/notifications', data);
    return response.data;
  },
  
  markAsRead: async (id) => {
    const response = await apiClient.put(`/notifications/${id}/read`);
    return response.data;
  },
  
  markAllAsRead: async () => {
    const response = await apiClient.put('/notifications/read-all');
    return response.data;
  },
};

export default apiClient;