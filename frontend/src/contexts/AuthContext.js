import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('accessToken'));

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('accessToken');

      if (storedToken) {
        try {
          const userData = await authAPI.getCurrentUser();
          setUser(userData);
          setToken(storedToken);
        } catch (error) {
          console.error('Token validation failed:', error);
          localStorage.removeItem('accessToken');
          setUser(null);
          setToken(null);
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email, password) => {
    try {
      setLoading(true);
      const response = await authAPI.login(email, password);

      if (!response.access_token) {
        throw new Error('No access token received');
      }

      localStorage.setItem('accessToken', response.access_token);
      
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
      setToken(response.access_token);

      toast.success('Login successful!');
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      const errorMessage = error.message || error.response?.data?.detail || 'Login failed';
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      const response = await authAPI.register(userData);
      toast.success('Registration successful! Please login.');
      return { success: true, data: response };
    } catch (error) {
      console.error('Registration error:', error);
      const errorMessage = error.message || 'Registration failed';
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    setUser(null);
    setToken(null);
    toast.success('Logged out successfully');
  };

  const updateUser = (updatedUserData) => {
    setUser(prevUser => ({ ...prevUser, ...updatedUserData }));
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    updateUser,
    isAuthenticated: !!user,
    isStudent: user?.role === 'student',
    isTeacher: user?.role === 'teacher',
    isAdmin: user?.role === 'admin',
    isAnalyst: user?.role === 'analyst',
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};