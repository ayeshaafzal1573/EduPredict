import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';

// Components
import Layout from './components/Layout/Layout';
import LoadingSpinner from './components/Common/LoadingSpinner';

// Pages
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import StudentDashboard from './pages/Student/Dashboard';
import TeacherDashboard from './pages/Teacher/Dashboard';
import AdminDashboard from './pages/Admin/Dashboard';
import AnalystDashboard from './pages/Analyst/Dashboard';
import Profile from './pages/Common/Profile';
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
                
                {/* Student Routes */}
                <Route
                  path="grades"
                  element={
                    <ProtectedRoute allowedRoles={['student']}>
                      <div>Student Grades Page</div>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="attendance"
                  element={
                    <ProtectedRoute allowedRoles={['student']}>
                      <div>Student Attendance Page</div>
                    </ProtectedRoute>
                  }
                />

                {/* Teacher Routes */}
                <Route
                  path="students"
                  element={
                    <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                      <div>Students Management Page</div>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="courses"
                  element={
                    <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                      <div>Courses Management Page</div>
                    </ProtectedRoute>
                  }
                />

                {/* Admin Routes */}
                <Route
                  path="users"
                  element={
                    <ProtectedRoute allowedRoles={['admin']}>
                      <div>Users Management Page</div>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="system"
                  element={
                    <ProtectedRoute allowedRoles={['admin']}>
                      <div>System Settings Page</div>
                    </ProtectedRoute>
                  }
                />

                {/* Analyst Routes */}
                <Route
                  path="analytics"
                  element={
                    <ProtectedRoute allowedRoles={['analyst', 'admin']}>
                      <div>Advanced Analytics Page</div>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="reports"
                  element={
                    <ProtectedRoute allowedRoles={['analyst', 'admin']}>
                      <div>Reports Page</div>
                    </ProtectedRoute>
                  }
                />
              </Route>

              {/* Error Routes */}
              <Route path="/unauthorized" element={<div className="text-center mt-20">Unauthorized Access</div>} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
