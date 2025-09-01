import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,PATCH,OPTIONS',

  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (only handle 401 → logout)
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: async (email, password) => {
    const response = await apiClient.post('/auth/login', { email, password });
    const { access_token } = response.data;

    // Save to localStorage for interceptors
    if (access_token) {
      localStorage.setItem('accessToken', access_token);
    }

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
    // Optional: await apiClient.post('/auth/logout');
  },
};


// Users API
export const usersAPI = {
  getUsers: async (params = {}) => {
    const response = await apiClient.get('/users/', { params });
    return response.data;
  },
  createUser: async (userData) => {
    const response = await apiClient.post('/users/', userData);
    return response.data;
  },
  getUserById: async (userId) => {
    const response = await apiClient.get(`/users/${userId}/`);
    return response.data;
  },

  updateUser: async (userId, userData) => {
    const response = await apiClient.put(`/users/${userId}/`, userData);
    return response.data;
  },

  deleteUser: async (userId) => {
    const response = await apiClient.delete(`/users/${userId}/`);
    return response.data;
  },
};


// Students API
export const studentsAPI = {
  getStudents: async (params = {}) => {
    const response = await apiClient.get('/students', { params });
    return response.data;
  },

  getStudentById: async (studentId) => {
    const response = await apiClient.get(`/students/${studentId}`);
    return response.data;
  },

  createStudent: async (studentData) => {
    const response = await apiClient.post('/students', studentData);
    return response.data;
  },

  updateStudent: async (studentId, studentData) => {
    const response = await apiClient.put(`/students/${studentId}`, studentData);
    return response.data;
  },

  getStudentPerformance: async (studentId) => {
    const response = await apiClient.get(`/students/${studentId}/performance`);
    return response.data;
  },

  getStudentAnalytics: async (studentId) => {
    const response = await apiClient.get(`/students/${studentId}/analytics`);
    return response.data;
  },
};

// Courses API
export const coursesAPI = {
  getCourses: async (params = {}) => {
    const response = await apiClient.get('/courses', { params });
    return response.data;
  },

  getCourseById: async (courseId) => {
    const response = await apiClient.get(`/courses/${courseId}`);
    return response.data;
  },

  createCourse: async (courseData) => {
    const response = await apiClient.post('/courses', courseData);
    return response.data;
  },

  updateCourse: async (courseId, courseData) => {
    const response = await apiClient.put(`/courses/${courseId}`, courseData);
    return response.data;
  },

  deleteCourse: async (courseId) => {
    const response = await apiClient.delete(`/courses/${courseId}`);
    return response.data;
  },
};

// Attendance API
export const attendanceAPI = {
  getAttendance: async (params = {}) => {
    const response = await apiClient.get('/attendance', { params });
    return response.data;
  },

  markAttendance: async (attendanceData) => {
    const response = await apiClient.post('/attendance', attendanceData);
    return response.data;
  },

  updateAttendance: async (attendanceId, attendanceData) => {
    const response = await apiClient.put(`/attendance/${attendanceId}`, attendanceData);
    return response.data;
  },

  getStudentAttendance: async (studentId, params = {}) => {
    const response = await apiClient.get(`/attendance/student/${studentId}`, { params });
    return response.data;
  },
};

// Grades API
export const gradesAPI = {
  getGrades: async (params = {}) => {
    const response = await apiClient.get('/grades', { params });
    return response.data;
  },

  createGrade: async (gradeData) => {
    const response = await apiClient.post('/grades', gradeData);
    return response.data;
  },

  updateGrade: async (gradeId, gradeData) => {
    const response = await apiClient.put(`/grades/${gradeId}`, gradeData);
    return response.data;
  },

  getStudentGrades: async (studentId, params = {}) => {
    const response = await apiClient.get(`/grades/student/${studentId}`, { params });
    return response.data;
  },
};

// Analytics API
export const analyticsAPI = {
  getDropoutPrediction: async (studentId) => {
    const response = await apiClient.get(`/analytics/dropout-prediction/${studentId}`);
    return response.data;
  },

  getGradePrediction: async (studentId, courseId) => {
    const response = await apiClient.get(`/analytics/grade-prediction/${studentId}/${courseId}`);
    return response.data;
  },

  getPerformanceTrends: async (params = {}) => {
    const response = await apiClient.get('/analytics/performance-trends', { params });
    return response.data;
  },

  getDashboardStats: async (role) => {
    const response = await apiClient.get(`/analytics/dashboard-stats/${role}`);
    return response.data;
  },

  getClassAnalytics: async (classId) => {
    const response = await apiClient.get(`/analytics/class/${classId}`);
    return response.data;
  },
};

// Notifications API
export const notificationsAPI = {
  getNotifications: async (params = {}) => {
    const response = await apiClient.get('/notifications', { params });
    return response.data;
  },

  markAsRead: async (notificationId) => {
    const response = await apiClient.put(`/notifications/${notificationId}/read`);
    return response.data;
  },

  markAllAsRead: async () => {
    const response = await apiClient.put('/notifications/read-all');
    return response.data;
  },

  deleteNotification: async (notificationId) => {
    const response = await apiClient.delete(`/notifications/${notificationId}`);
    return response.data;
  },
};

export default apiClient;
