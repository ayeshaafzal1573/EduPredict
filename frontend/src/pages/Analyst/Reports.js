import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { analyticsAPI } from '../../services/api';
import toast from 'react-hot-toast';

const AnalystReports = () => {
  const { user } = useAuth();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReports();
  }, [user]);

  const fetchReports = async () => {
    try {
      setLoading(true);
      // Mock reports data
      setReports([
        { id: 1, name: 'Student Performance Report', type: 'performance', date: '2024-01-15' },
        { id: 2, name: 'Dropout Risk Analysis', type: 'risk', date: '2024-01-14' },
        { id: 3, name: 'Attendance Trends', type: 'attendance', date: '2024-01-13' }
      ]);
    } catch (err) {
      toast.error('Failed to load reports');
    } finally {
      setLoading(false);
    }
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

  return (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">📈 Analytics Reports</h1>
        <p className="text-purple-100 text-lg">Generate and view comprehensive analytics reports</p>
      </div>
      
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Available Reports</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reports.map((report) => (
            <div key={report.id} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
              <h3 className="font-semibold text-gray-800">{report.name}</h3>
              <p className="text-sm text-gray-600">{report.type}</p>
              <p className="text-xs text-gray-500">{report.date}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AnalystReports;
