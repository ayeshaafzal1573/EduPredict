import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';

// Components
import Layout from './components/Layout/Layout';
import LoadingSpinner from './components/Common/LoadingSpinner';

// Auth Pages
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';

// Dashboard Pages
import StudentDashboard from './pages/Student/Dashboard';
import TeacherDashboard from './pages/Teacher/Dashboard';
import AdminDashboard from './pages/Admin/Dashboard';
import AnalystDashboard from './pages/Analyst/Dashboard';

// Student Pages
import StudentPerformance from './pages/Student/Performance';
import StudentPredictions from './pages/Student/Predictions';
import StudentAttendance from './pages/Student/Attendance';
import StudentCourses from './pages/Student/Courses';

// Teacher Pages
import TeacherClasses from './pages/Teacher/Classes';
import TeacherGrades from './pages/Teacher/Grades';
import TeacherAttendance from './pages/Teacher/Attendance';

// Admin Pages
import AdminUsers from './pages/Admin/Users';
import AdminCourses from './pages/Admin/Courses';
import AdminAnalytics from './pages/Admin/Analytics';

// Analyst Pages
import AnalystModels from './pages/Analyst/Models';
import AnalystReports from './pages/Analyst/Reports';
import AnalystPredictions from './pages/Analyst/Predictions';

// Common Pages
import Profile from './pages/Common/Profile';
import Settings from './pages/Common/Settings';
import Help from './pages/Common/Help';
import NotFound from './pages/Common/NotFound';

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

// Dashboard Router Component
const DashboardRouter = () => {
  const { user } = useAuth();

  switch (user?.role) {
    case 'student':
      return <StudentDashboard />;
    case 'teacher':
      return <TeacherDashboard />;
    case 'admin':
      return <AdminDashboard />;
    case 'analyst':
      return <AnalystDashboard />;
    default:
      return <Navigate to="/login" replace />;
  }
};

// Public Route Component (redirect if authenticated)
const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <div className="App min-h-screen bg-gray-50">
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
                success: {
                  duration: 3000,
                  theme: {
                    primary: '#22c55e',
                    secondary: '#16a34a',
                  },
                },
                error: {
                  duration: 5000,
                  theme: {
                    primary: '#ef4444',
                    secondary: '#dc2626',
                  },
                },
              }}
            />

            <Routes>
              {/* Public Routes */}
              <Route
                path="/login"
                element={
                  <PublicRoute>
                    <Login />
                  </PublicRoute>
                }
              />
              <Route
                path="/register"
                element={
                  <PublicRoute>
                    <Register />
                  </PublicRoute>
                }
              />

              {/* Protected Routes */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Layout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardRouter />} />
                <Route path="profile" element={<Profile />} />
                <Route path="settings" element={<Settings />} />
                <Route path="help" element={<Help />} />

                {/* Student Routes */}
                <Route
                  path="performance"
                  element={
                    <ProtectedRoute allowedRoles={['student']}>
                      <StudentPerformance />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="predictions"
                  element={
                    <ProtectedRoute allowedRoles={['student']}>
                      <StudentPredictions />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="attendance"
                  element={
                    <ProtectedRoute allowedRoles={['student']}>
                      <StudentAttendance />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="student-courses"
                  element={
                    <ProtectedRoute allowedRoles={['student']}>
                      <StudentCourses />
                    </ProtectedRoute>
                  }
                />

                {/* Teacher Routes */}
                <Route
                  path="classes"
                  element={
                    <ProtectedRoute allowedRoles={['teacher']}>
                      <TeacherClasses />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="grades"
                  element={
                    <ProtectedRoute allowedRoles={['teacher']}>
                      <TeacherGrades />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="teacher-attendance"
                  element={
                    <ProtectedRoute allowedRoles={['teacher']}>
                      <TeacherAttendance />
                    </ProtectedRoute>
                  }
                />
            
             

                {/* Admin Routes */}
                <Route
                  path="users"
                  element={
                    <ProtectedRoute allowedRoles={['admin']}>
                      <AdminUsers />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="admin-courses"
                  element={
                    <ProtectedRoute allowedRoles={['admin']}>
                      <AdminCourses />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="admin-analytics"
                  element={
                    <ProtectedRoute allowedRoles={['admin']}>
                      <AdminAnalytics />
                    </ProtectedRoute>
                  }
                />
              

                {/* Analyst Routes */}
                <Route
                  path="models"
                  element={
                    <ProtectedRoute allowedRoles={['analyst']}>
                      <AnalystModels />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="reports"
                  element={
                    <ProtectedRoute allowedRoles={['analyst']}>
                      <AnalystReports />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="analyst-predictions"
                  element={
                    <ProtectedRoute allowedRoles={['analyst']}>
                      <AnalystPredictions />
                    </ProtectedRoute>
                  }
                />
             
              </Route>

              {/* Error Routes */}
              <Route path="/unauthorized" element={
                <div className="min-h-screen flex items-center justify-center bg-gray-50">
                  <div className="text-center">
                    <div className="text-red-500 text-6xl mb-4">🚫</div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">Unauthorized Access</h1>
                    <p className="text-gray-600 mb-4">You don't have permission to access this page.</p>
                    <button
                      onClick={() => window.history.back()}
                      className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg"
                    >
                      Go Back
                    </button>
                  </div>
                </div>
              } />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;