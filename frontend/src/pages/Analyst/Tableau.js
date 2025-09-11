import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { analyticsAPI } from '../../services/api';
import toast from 'react-hot-toast';

const AnalystTableau = () => {
  const { user } = useAuth();
  const [dashboards, setDashboards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDashboard, setSelectedDashboard] = useState(null);

  useEffect(() => {
    fetchTableauDashboards();
  }, [user]);

  const fetchTableauDashboards = async () => {
    try {
      setLoading(true);
      setError(null);

      // Mock Tableau dashboards data
      const mockDashboards = [
        {
          id: 'student_performance_dashboard',
          name: 'Student Performance Dashboard',
          description: 'Comprehensive view of student academic performance across all departments',
          category: 'Academic',
          lastUpdated: '2024-01-15T10:30:00Z',
          views: 1250,
          status: 'active',
          thumbnail: 'https://images.pexels.com/photos/590022/pexels-photo-590022.jpeg?auto=compress&cs=tinysrgb&w=400',
          metrics: ['GPA Trends', 'Course Performance', 'Grade Distribution', 'Semester Comparison'],
          filters: ['Department', 'Academic Year', 'Student Cohort', 'Course Level']
        },
        {
          id: 'dropout_risk_dashboard',
          name: 'Dropout Risk Analysis',
          description: 'Real-time dropout risk assessment and intervention tracking',
          category: 'Risk Management',
          lastUpdated: '2024-01-14T15:45:00Z',
          views: 890,
          status: 'active',
          thumbnail: 'https://images.pexels.com/photos/669610/pexels-photo-669610.jpeg?auto=compress&cs=tinysrgb&w=400',
          metrics: ['Risk Scores', 'Factor Analysis', 'Intervention Tracking', 'Success Rates'],
          filters: ['Risk Level', 'Department', 'Semester', 'Intervention Type']
        },
        {
          id: 'attendance_analytics_dashboard',
          name: 'Attendance Analytics',
          description: 'Detailed attendance patterns and correlation with academic performance',
          category: 'Attendance',
          lastUpdated: '2024-01-13T09:20:00Z',
          views: 675,
          status: 'active',
          thumbnail: 'https://images.pexels.com/photos/301926/pexels-photo-301926.jpeg?auto=compress&cs=tinysrgb&w=400',
          metrics: ['Attendance Rates', 'Trend Analysis', 'Course Comparison', 'Impact Assessment'],
          filters: ['Course', 'Time Period', 'Day of Week', 'Weather Conditions']
        },
        {
          id: 'institutional_overview_dashboard',
          name: 'Institutional Overview',
          description: 'High-level institutional metrics and KPIs for executive reporting',
          category: 'Executive',
          lastUpdated: '2024-01-12T14:15:00Z',
          views: 420,
          status: 'active',
          thumbnail: 'https://images.pexels.com/photos/669619/pexels-photo-669619.jpeg?auto=compress&cs=tinysrgb&w=400',
          metrics: ['Enrollment Trends', 'Retention Rates', 'Financial Metrics', 'Faculty Performance'],
          filters: ['Academic Year', 'Department', 'Program Type', 'Campus Location']
        },
        {
          id: 'predictive_analytics_dashboard',
          name: 'Predictive Analytics Hub',
          description: 'Advanced predictive models and forecasting for strategic planning',
          category: 'Predictive',
          lastUpdated: '2024-01-11T11:00:00Z',
          views: 320,
          status: 'development',
          thumbnail: 'https://images.pexels.com/photos/669615/pexels-photo-669615.jpeg?auto=compress&cs=tinysrgb&w=400',
          metrics: ['Future Enrollment', 'Resource Planning', 'Budget Forecasting', 'Capacity Planning'],
          filters: ['Forecast Period', 'Confidence Level', 'Scenario Type', 'Department']
        },
        {
          id: 'faculty_analytics_dashboard',
          name: 'Faculty Analytics',
          description: 'Teaching effectiveness and faculty performance metrics',
          category: 'Faculty',
          lastUpdated: '2024-01-10T16:30:00Z',
          views: 280,
          status: 'active',
          thumbnail: 'https://images.pexels.com/photos/1181533/pexels-photo-1181533.jpeg?auto=compress&cs=tinysrgb&w=400',
          metrics: ['Teaching Ratings', 'Student Outcomes', 'Course Effectiveness', 'Professional Development'],
          filters: ['Faculty Member', 'Department', 'Course Type', 'Evaluation Period']
        }
      ];

      setDashboards(mockDashboards);
    } catch (err) {
      console.error('Error fetching Tableau dashboards:', err);
      setError('Failed to load Tableau dashboards. Please try again.');
      toast.error('Failed to load dashboards');
    } finally {
      setLoading(false);
    }
  };

  const openDashboard = (dashboard) => {
    // In a real implementation, this would open the actual Tableau dashboard
    toast.success(`Opening ${dashboard.name} dashboard...`);
    setSelectedDashboard(dashboard);
  };

  const refreshDashboard = async (dashboardId) => {
    try {
      toast.loading('Refreshing dashboard data...', { id: 'refresh' });
      
      // Simulate dashboard refresh
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setDashboards(prev => prev.map(d => 
        d.id === dashboardId 
          ? { ...d, lastUpdated: new Date().toISOString() }
          : d
      ));

      toast.success('Dashboard refreshed successfully!', { id: 'refresh' });
    } catch (err) {
      console.error('Error refreshing dashboard:', err);
      toast.error('Failed to refresh dashboard', { id: 'refresh' });
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'development': return 'bg-yellow-100 text-yellow-800';
      case 'maintenance': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Academic': 'bg-blue-100 text-blue-800',
      'Risk Management': 'bg-red-100 text-red-800',
      'Attendance': 'bg-green-100 text-green-800',
      'Executive': 'bg-purple-100 text-purple-800',
      'Predictive': 'bg-indigo-100 text-indigo-800',
      'Faculty': 'bg-orange-100 text-orange-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Tableau dashboards...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">📊</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Tableau Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchTableauDashboards}
            className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Reload Dashboards
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">📊 Tableau Integration</h1>
        <p className="text-purple-100 text-lg">Advanced data visualization with Tableau dashboards</p>
      </div>

      {/* Dashboard Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Total Dashboards</p>
              <p className="text-3xl font-bold">{dashboards.length}</p>
            </div>
            <div className="text-4xl opacity-80">📊</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Active Dashboards</p>
              <p className="text-3xl font-bold">{dashboards.filter(d => d.status === 'active').length}</p>
            </div>
            <div className="text-4xl opacity-80">✅</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Total Views</p>
              <p className="text-3xl font-bold">{dashboards.reduce((sum, d) => sum + d.views, 0).toLocaleString()}</p>
            </div>
            <div className="text-4xl opacity-80">👁️</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">Last Updated</p>
              <p className="text-3xl font-bold">Today</p>
            </div>
            <div className="text-4xl opacity-80">🔄</div>
          </div>
        </div>
      </div>

      {/* Dashboards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dashboards.map((dashboard) => (
          <div key={dashboard.id} className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20 hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
            <div className="relative mb-4">
              <img
                src={dashboard.thumbnail}
                alt={dashboard.name}
                className="w-full h-32 object-cover rounded-xl"
              />
              <div className="absolute top-2 right-2 flex space-x-2">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(dashboard.status)}`}>
                  {dashboard.status}
                </span>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(dashboard.category)}`}>
                  {dashboard.category}
                </span>
              </div>
            </div>

            <div className="mb-4">
              <h3 className="text-xl font-bold text-gray-800 mb-2">{dashboard.name}</h3>
              <p className="text-gray-600 text-sm">{dashboard.description}</p>
            </div>

            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Views:</span>
                <span className="font-medium text-gray-800">{dashboard.views.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Last Updated:</span>
                <span className="font-medium text-gray-800">
                  {new Date(dashboard.lastUpdated).toLocaleDateString()}
                </span>
              </div>
            </div>

            <div className="mb-4">
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Key Metrics:</h4>
              <div className="flex flex-wrap gap-1">
                {dashboard.metrics.slice(0, 3).map((metric, index) => (
                  <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    {metric}
                  </span>
                ))}
                {dashboard.metrics.length > 3 && (
                  <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                    +{dashboard.metrics.length - 3} more
                  </span>
                )}
              </div>
            </div>

            <div className="flex space-x-2">
              <button
                onClick={() => openDashboard(dashboard)}
                disabled={dashboard.status !== 'active'}
                className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white px-3 py-2 rounded-lg text-sm font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200 disabled:opacity-50"
              >
                Open Dashboard
              </button>
              <button
                onClick={() => refreshDashboard(dashboard.id)}
                className="px-3 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50 transition-colors"
              >
                🔄
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Dashboard Categories */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h2 className="text-xl font-bold text-gray-800 mb-6">Dashboard Categories</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { name: 'Academic Performance', count: 2, icon: '📚', color: 'from-blue-500 to-blue-600' },
            { name: 'Risk Management', count: 1, icon: '⚠️', color: 'from-red-500 to-red-600' },
            { name: 'Attendance Tracking', count: 1, icon: '📅', color: 'from-green-500 to-green-600' },
            { name: 'Executive Reports', count: 1, icon: '📊', color: 'from-purple-500 to-purple-600' },
            { name: 'Predictive Analytics', count: 1, icon: '🔮', color: 'from-indigo-500 to-indigo-600' },
            { name: 'Faculty Analytics', count: 1, icon: '👨‍🏫', color: 'from-orange-500 to-orange-600' }
          ].map((category, index) => (
            <div key={index} className={`p-4 bg-gradient-to-r ${category.color} text-white rounded-xl`}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl mb-1">{category.icon}</div>
                  <div className="font-semibold">{category.name}</div>
                  <div className="text-sm opacity-90">{category.count} dashboard{category.count !== 1 ? 's' : ''}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tableau Server Connection */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h2 className="text-xl font-bold text-gray-800 mb-6">Tableau Server Connection</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-gray-700">Server Status: Connected</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-gray-700">Data Source: MongoDB + HDFS</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
              <span className="text-gray-700">Last Sync: {new Date().toLocaleTimeString()}</span>
            </div>
          </div>

          <div className="space-y-4">
            <button className="w-full bg-gradient-to-r from-green-500 to-green-600 text-white px-4 py-2 rounded-lg font-medium hover:from-green-600 hover:to-green-700 transition-all duration-200">
              📊 Open Tableau Server
            </button>
            <button className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200">
              🔄 Sync Data Sources
            </button>
            <button className="w-full bg-gradient-to-r from-purple-500 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:from-purple-600 hover:to-purple-700 transition-all duration-200">
              ⚙️ Configure Connection
            </button>
          </div>
        </div>
      </div>

      {/* Dashboard Preview Modal */}
      {selectedDashboard && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-800">{selectedDashboard.name}</h2>
              <button
                onClick={() => setSelectedDashboard(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="space-y-6">
              <div className="bg-gray-100 rounded-xl p-8 text-center">
                <div className="text-6xl mb-4">📊</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Tableau Dashboard Preview</h3>
                <p className="text-gray-600 mb-4">{selectedDashboard.description}</p>
                <button className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg font-medium transition-colors">
                  Open in Tableau
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">Available Metrics</h4>
                  <div className="space-y-2">
                    {selectedDashboard.metrics.map((metric, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span className="text-sm text-gray-600">{metric}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">Available Filters</h4>
                  <div className="space-y-2">
                    {selectedDashboard.filters.map((filter, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-sm text-gray-600">{filter}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalystTableau;