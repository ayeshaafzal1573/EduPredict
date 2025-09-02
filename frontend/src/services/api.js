// api.js
import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Attach token dynamically from localStorage for all requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle 401 → logout
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

export default apiClient;

// -------------------- AUTH API --------------------
export const authAPI = {
  login: async (email, password) => {
    const response = await apiClient.post('/auth/login', { email, password });
    const { access_token } = response.data;
    if (access_token) localStorage.setItem('accessToken', access_token);
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

// -------------------- USERS API --------------------
export const usersAPI = {
  getUsers: async (params = {}) => (await apiClient.get('/users/', { params })).data,
  createUser: async (data) => (await apiClient.post('/users/', data)).data,
  getUserById: async (id) => (await apiClient.get(`/users/${id}/`)).data,
  updateUser: async (id, data) => (await apiClient.put(`/users/${id}/`, data)).data,
  deleteUser: async (id) => (await apiClient.delete(`/users/${id}/`)).data,
};

// -------------------- STUDENTS API --------------------
export const studentsAPI = {
  getStudents: async (params = {}) => (await apiClient.get('/students', { params })).data,
  getStudentById: async (id) => (await apiClient.get(`/students/${id}`)).data,
  createStudent: async (data) => (await apiClient.post('/students', data)).data,
  updateStudent: async (id, data) => (await apiClient.put(`/students/${id}`, data)).data,
  getStudentPerformance: async (id) => (await apiClient.get(`/students/${id}/performance`)).data,
  getStudentAnalytics: async (id) => (await apiClient.get(`/students/${id}/analytics`)).data,
};

// -------------------- COURSES API --------------------
export const coursesAPI = {
  getCourses: async (params = {}) => (await apiClient.get('/courses', { params })).data,
  getCourseById: async (id) => (await apiClient.get(`/courses/${id}`)).data,
  createCourse: async (data) => (await apiClient.post('/courses', data)).data,
  updateCourse: async (id, data) => (await apiClient.put(`/courses/${id}`, data)).data,
  deleteCourse: async (id) => (await apiClient.delete(`/courses/${id}`)).data,
};

// -------------------- ATTENDANCE API --------------------
export const attendanceAPI = {
  getAttendance: async (params = {}) => (await apiClient.get('/attendance', { params })).data,
  markAttendance: async (data) => (await apiClient.post('/attendance', data)).data,
  updateAttendance: async (id, data) => (await apiClient.put(`/attendance/${id}`, data)).data,
  getStudentAttendance: async (studentId, params = {}) => (await apiClient.get(`/attendance/student/${studentId}`, { params })).data,
};

// -------------------- GRADES API --------------------
export const gradesAPI = {
  getGrades: async (params = {}) => (await apiClient.get('/grades', { params })).data,
  createGrade: async (data) => (await apiClient.post('/grades', data)).data,
  updateGrade: async (id, data) => (await apiClient.put(`/grades/${id}`, data)).data,
  getStudentGrades: async (studentId, params = {}) => (await apiClient.get(`/grades/student/${studentId}`, { params })).data,
};

// -------------------- ANALYTICS API --------------------
export const analyticsAPI = {
  getDropoutPrediction: async (studentId) => (await apiClient.get(`/analytics/dropout-prediction/${studentId}`)).data,
  getGradePrediction: async (studentId, courseId) => (await apiClient.get(`/analytics/grade-prediction/${studentId}/${courseId}`)).data,
  getPerformanceTrends: async (params = {}) => (await apiClient.get('/analytics/performance-trends', { params })).data,
  getDashboardStats: async (role) => (await apiClient.get(`/analytics/dashboard-stats/${role}`)).data,
  getClassAnalytics: async (classId) => (await apiClient.get(`/analytics/class/${classId}`)).data,
};

// -------------------- NOTIFICATIONS API --------------------
export const notificationsAPI = {
  getNotifications: async (params = {}) => (await apiClient.get('/notifications', { params })).data,
  markAsRead: async (id) => (await apiClient.put(`/notifications/${id}/read`)).data,
  markAllAsRead: async () => (await apiClient.put('/notifications/read-all')).data,
  deleteNotification: async (id) => (await apiClient.delete(`/notifications/${id}`)).data,
};
