import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { analyticsAPI } from '../../services/api';
import PerformanceChart from '../../components/Charts/PerformanceChart';
import toast from 'react-hot-toast';

const AnalystReports = () => {
  const { user } = useAuth();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [generatingReport, setGeneratingReport] = useState(false);

  useEffect(() => {
    fetchReports();
  }, [user]);

  const fetchReports = async () => {
    try {
      setLoading(true);
      setError(null);

      // Mock reports data with more comprehensive information
      const mockReports = [
        {
          id: 'student_performance_2024',
          name: 'Student Performance Analysis 2024',
          type: 'performance',
          description: 'Comprehensive analysis of student academic performance across all departments',
          date: '2024-01-15',
          status: 'completed',
          size: '2.3 MB',
          records: 15420,
          insights: [
            'Overall GPA increased by 0.15 points compared to 2023',
            'Computer Science department shows highest performance',
            'Attendance correlation with GPA is 0.78'
          ]
        },
        {
          id: 'dropout_risk_analysis_2024',
          name: 'Dropout Risk Analysis Q1 2024',
          type: 'risk',
          description: 'Detailed analysis of dropout risk factors and prediction accuracy',
          date: '2024-01-14',
          status: 'completed',
          size: '1.8 MB',
          records: 8750,
          insights: [
            '12% of students identified as high-risk',
            'Early intervention reduced dropout rate by 23%',
            'Financial aid status is a significant predictor'
          ]
        },
        {
          id: 'attendance_trends_2024',
          name: 'Attendance Trends & Patterns',
          type: 'attendance',
          description: 'Analysis of attendance patterns and their impact on academic outcomes',
          date: '2024-01-13',
          status: 'completed',
          size: '3.1 MB',
          records: 45200,
          insights: [
            'Monday classes have lowest attendance (78%)',
            'Online classes show 15% higher attendance',
            'Weather significantly impacts attendance rates'
          ]
        },
        {
          id: 'ml_model_performance_2024',
          name: 'ML Model Performance Report',
          type: 'model',
          description: 'Evaluation of machine learning model accuracy and performance metrics',
          date: '2024-01-12',
          status: 'completed',
          size: '1.2 MB',
          records: 25000,
          insights: [
            'Dropout prediction model achieved 87.2% accuracy',
            'Grade prediction model improved to 82.4% accuracy',
            'Feature importance analysis reveals top predictors'
          ]
        },
        {
          id: 'department_comparison_2024',
          name: 'Department Performance Comparison',
          type: 'comparison',
          description: 'Comparative analysis of academic performance across departments',
          date: '2024-01-10',
          status: 'generating',
          size: 'Generating...',
          records: 0,
          insights: []
        },
        {
          id: 'intervention_effectiveness_2024',
          name: 'Intervention Effectiveness Study',
          type: 'intervention',
          description: 'Analysis of academic intervention programs and their success rates',
          date: '2024-01-08',
          status: 'completed',
          size: '2.7 MB',
          records: 3420,
          insights: [
            'Tutoring programs increased GPA by average 0.4 points',
            'Peer mentoring shows 67% success rate',
            'Early warning systems reduced failures by 31%'
          ]
        }
      ];

      setReports(mockReports);
    } catch (err) {
      console.error('Error fetching reports:', err);
      setError('Failed to load reports. Please try again.');
      toast.error('Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async (reportType) => {
    try {
      setGeneratingReport(true);
      toast.loading('Generating report...', { id: 'generating' });

      // Simulate report generation
      await new Promise(resolve => setTimeout(resolve, 3000));

      const newReport = {
        id: `${reportType}_${Date.now()}`,
        name: `${reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report`,
        type: reportType,
        description: `Generated ${reportType} analysis report`,
        date: new Date().toISOString().split('T')[0],
        status: 'completed',
        size: '1.5 MB',
        records: Math.floor(Math.random() * 10000) + 5000,
        insights: [
          'Report generated successfully',
          'Data analysis completed',
          'Insights extracted from latest data'
        ]
      };

      setReports(prev => [newReport, ...prev]);
      toast.success('Report generated successfully!', { id: 'generating' });
    } catch (err) {
      console.error('Error generating report:', err);
      toast.error('Failed to generate report', { id: 'generating' });
    } finally {
      setGeneratingReport(false);
    }
  };

  const viewReportDetails = async (report) => {
    try {
      setSelectedReport(report);
      
      // Mock detailed report data
      const mockDetailedData = {
        summary: {
          totalStudents: 1250,
          averageGPA: 3.15,
          attendanceRate: 84.2,
          completionRate: 89.5
        },
        trends: [
          { month: 'Sep', gpa: 3.1, attendance: 85, enrollment: 1200 },
          { month: 'Oct', gpa: 3.12, attendance: 83, enrollment: 1220 },
          { month: 'Nov', gpa: 3.15, attendance: 84, enrollment: 1240 },
          { month: 'Dec', gpa: 3.18, attendance: 86, enrollment: 1250 },
          { month: 'Jan', gpa: 3.15, attendance: 84, enrollment: 1250 }
        ],
        departmentBreakdown: [
          { name: 'Computer Science', students: 450, avgGPA: 3.25, retention: 92 },
          { name: 'Engineering', students: 380, avgGPA: 3.18, retention: 89 },
          { name: 'Mathematics', students: 220, avgGPA: 3.05, retention: 85 },
          { name: 'Physics', students: 200, avgGPA: 3.12, retention: 87 }
        ]
      };

      setReportData(mockDetailedData);
    } catch (err) {
      console.error('Error loading report details:', err);
      toast.error('Failed to load report details');
    }
  };

  const downloadReport = async (reportId) => {
    try {
      toast.loading('Preparing download...', { id: 'download' });
      
      // Simulate download preparation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast.success('Download started!', { id: 'download' });
    } catch (err) {
      console.error('Error downloading report:', err);
      toast.error('Failed to download report', { id: 'download' });
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'generating': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeColor = (type) => {
    const colors = {
      performance: 'bg-blue-100 text-blue-800',
      risk: 'bg-red-100 text-red-800',
      attendance: 'bg-green-100 text-green-800',
      model: 'bg-purple-100 text-purple-800',
      comparison: 'bg-orange-100 text-orange-800',
      intervention: 'bg-indigo-100 text-indigo-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading reports...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">📈</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Reports Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchReports}
            className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Reload Reports
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">📈 Analytics Reports</h1>
        <p className="text-purple-100 text-lg">Generate and view comprehensive analytics reports</p>
      </div>

      {/* Quick Actions */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Generate New Report</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { type: 'performance', name: 'Performance Analysis', icon: '📊', color: 'from-blue-500 to-blue-600' },
            { type: 'risk', name: 'Risk Assessment', icon: '⚠️', color: 'from-red-500 to-red-600' },
            { type: 'attendance', name: 'Attendance Report', icon: '📅', color: 'from-green-500 to-green-600' },
            { type: 'model', name: 'Model Performance', icon: '🤖', color: 'from-purple-500 to-purple-600' }
          ].map((reportType) => (
            <button
              key={reportType.type}
              onClick={() => generateReport(reportType.type)}
              disabled={generatingReport}
              className={`p-4 bg-gradient-to-r ${reportType.color} text-white rounded-xl hover:shadow-lg transition-all duration-200 transform hover:scale-105 disabled:opacity-50`}
            >
              <div className="text-2xl mb-2">{reportType.icon}</div>
              <div className="text-sm font-medium">{reportType.name}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Reports List */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h2 className="text-xl font-bold text-gray-800 mb-6">Available Reports</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {reports.map((report) => (
            <div key={report.id} className="bg-gradient-to-br from-white/60 to-white/40 rounded-xl p-6 border border-white/30 hover:shadow-lg transition-all duration-200">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-gray-800 mb-1">{report.name}</h3>
                  <p className="text-sm text-gray-600">{report.description}</p>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(report.status)}`}>
                  {report.status}
                </span>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Type:</span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeColor(report.type)}`}>
                    {report.type}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Date:</span>
                  <span className="text-gray-800">{new Date(report.date).toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Size:</span>
                  <span className="text-gray-800">{report.size}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Records:</span>
                  <span className="text-gray-800">{report.records.toLocaleString()}</span>
                </div>
              </div>

              {report.insights.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Key Insights:</h4>
                  <ul className="text-xs text-gray-600 space-y-1">
                    {report.insights.slice(0, 2).map((insight, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-blue-500 mr-1">•</span>
                        {insight}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="flex space-x-2">
                <button
                  onClick={() => viewReportDetails(report)}
                  className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white px-3 py-2 rounded-lg text-sm font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200"
                >
                  View Details
                </button>
                {report.status === 'completed' && (
                  <button
                    onClick={() => downloadReport(report.id)}
                    className="px-3 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50 transition-colors"
                  >
                    📥 Download
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Report Details Modal */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-800">{selectedReport.name}</h2>
              <button
                onClick={() => setSelectedReport(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Report Summary */}
              <div className="lg:col-span-1">
                <div className="bg-gray-50 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Report Summary</h3>
                  <div className="space-y-3">
                    <div>
                      <span className="text-sm text-gray-500">Status</span>
                      <div className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(selectedReport.status)} ml-2`}>
                        {selectedReport.status}
                      </div>
                    </div>
                    <div>
                      <span className="text-sm text-gray-500">Generated</span>
                      <p className="font-medium">{new Date(selectedReport.date).toLocaleDateString()}</p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-500">Records Analyzed</span>
                      <p className="font-medium">{selectedReport.records.toLocaleString()}</p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-500">File Size</span>
                      <p className="font-medium">{selectedReport.size}</p>
                    </div>
                  </div>

                  <div className="mt-6">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Key Insights</h4>
                    <ul className="text-sm text-gray-600 space-y-2">
                      {selectedReport.insights.map((insight, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-blue-500 mr-2">•</span>
                          {insight}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Report Visualizations */}
              <div className="lg:col-span-2">
                {reportData && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="bg-blue-50 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-blue-600">{reportData.summary.totalStudents}</div>
                        <div className="text-sm text-blue-700">Total Students</div>
                      </div>
                      <div className="bg-green-50 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-green-600">{reportData.summary.averageGPA}</div>
                        <div className="text-sm text-green-700">Average GPA</div>
                      </div>
                      <div className="bg-yellow-50 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-yellow-600">{reportData.summary.attendanceRate}%</div>
                        <div className="text-sm text-yellow-700">Attendance</div>
                      </div>
                      <div className="bg-purple-50 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-purple-600">{reportData.summary.completionRate}%</div>
                        <div className="text-sm text-purple-700">Completion</div>
                      </div>
                    </div>

                    <PerformanceChart
                      title="Performance Trends"
                      data={reportData.trends}
                      type="line"
                    />

                    <div className="bg-gray-50 rounded-xl p-6">
                      <h4 className="text-lg font-semibold text-gray-800 mb-4">Department Breakdown</h4>
                      <div className="space-y-3">
                        {reportData.departmentBreakdown.map((dept, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-white rounded-lg">
                            <div>
                              <div className="font-medium text-gray-900">{dept.name}</div>
                              <div className="text-sm text-gray-500">{dept.students} students</div>
                            </div>
                            <div className="text-right">
                              <div className="font-semibold text-gray-800">GPA: {dept.avgGPA}</div>
                              <div className="text-sm text-green-600">Retention: {dept.retention}%</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalystReports;