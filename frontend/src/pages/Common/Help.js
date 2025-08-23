import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const Help = () => {
  const { user } = useAuth();
  const [activeSection, setActiveSection] = useState('getting-started');
  const [searchTerm, setSearchTerm] = useState('');

  const helpSections = {
    'getting-started': {
      title: 'Getting Started',
      icon: '🚀',
      content: [
        {
          question: 'How do I log in to EduPredict?',
          answer: 'Use your institutional email and password provided by your administrator. If you forgot your password, click "Forgot Password" on the login page.'
        },
        {
          question: 'What can I do with my dashboard?',
          answer: 'Your dashboard provides an overview of your academic progress, upcoming assignments, and personalized insights based on your role (Student, Teacher, Admin, or Analyst).'
        },
        {
          question: 'How do I navigate the system?',
          answer: 'Use the sidebar navigation to access different sections. The menu items change based on your role and permissions.'
        }
      ]
    },
    'features': {
      title: 'Features Guide',
      icon: '⭐',
      content: [
        {
          question: 'What are AI Predictions?',
          answer: 'EduPredict uses machine learning to predict academic outcomes like dropout risk and final grades. These predictions help identify students who may need additional support.'
        },
        {
          question: 'How accurate are the predictions?',
          answer: 'Our dropout prediction model has 87% accuracy, and grade prediction has 82% accuracy. These are continuously improved with more data.'
        },
        {
          question: 'What is the Risk Assessment?',
          answer: 'Risk assessment identifies students who may be at risk of academic failure or dropping out based on various factors like attendance, grades, and engagement.'
        }
      ]
    },
    'troubleshooting': {
      title: 'Troubleshooting',
      icon: '🔧',
      content: [
        {
          question: 'I can\'t see my grades/courses',
          answer: 'Make sure you are enrolled in courses and that your instructor has posted grades. Contact your administrator if the issue persists.'
        },
        {
          question: 'The predictions seem incorrect',
          answer: 'Predictions are based on available data and patterns. They improve over time as more data is collected. Contact support if you notice consistent inaccuracies.'
        },
        {
          question: 'I\'m getting permission errors',
          answer: 'You may be trying to access features not available to your role. Contact your administrator to verify your permissions.'
        }
      ]
    },
    'account': {
      title: 'Account Management',
      icon: '👤',
      content: [
        {
          question: 'How do I change my password?',
          answer: 'Go to Settings > Security and use the "Change Password" form. You\'ll need your current password to set a new one.'
        },
        {
          question: 'How do I update my profile?',
          answer: 'Visit Settings > Profile to update your name, email, and other personal information.'
        },
        {
          question: 'Can I change my notification preferences?',
          answer: 'Yes, go to Settings > Notifications to customize which notifications you receive and how you receive them.'
        }
      ]
    }
  };

  const roleSpecificHelp = {
    student: [
      {
        question: 'How do I view my performance trends?',
        answer: 'Go to the Performance page to see your GPA trends, course grades, and academic progress over time.'
      },
      {
        question: 'What should I do if I\'m flagged as at-risk?',
        answer: 'Contact your advisor or instructor immediately. Review the risk factors and work on improving attendance, assignment completion, and engagement.'
      }
    ],
    teacher: [
      {
        question: 'How do I enter grades for my students?',
        answer: 'Go to Grades > Select your course > Add Assignment. You can enter grades individually or use bulk entry for efficiency.'
      },
      {
        question: 'How do I track student attendance?',
        answer: 'Use the Attendance page to mark attendance for each class session. You can mark students as present, absent, late, or excused.'
      }
    ],
    admin: [
      {
        question: 'How do I add new users to the system?',
        answer: 'Go to Users > Add New User. Fill in the required information and assign the appropriate role (Student, Teacher, Admin, or Analyst).'
      },
      {
        question: 'How do I create new courses?',
        answer: 'Navigate to Courses > Add New Course. Enter course details, assign a teacher, and set enrollment limits.'
      }
    ],
    analyst: [
      {
        question: 'How do I access ML model performance?',
        answer: 'Go to Models to view model accuracy, training status, and performance metrics. You can also retrain models from this page.'
      },
      {
        question: 'How do I generate reports?',
        answer: 'Use the Reports page to create custom analytics reports. You can filter by date range, department, or specific metrics.'
      }
    ]
  };

  const filteredSections = Object.entries(helpSections).filter(([key, section]) =>
    section.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    section.content.some(item => 
      item.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.answer.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">❓ Help & Support</h1>
        <p className="text-indigo-100 text-lg">
          Find answers to common questions and get help using EduPredict
        </p>
      </div>

      {/* Search */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
        <div className="relative">
          <input
            type="text"
            placeholder="Search help articles..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <span className="text-gray-400">🔍</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20 sticky top-4">
            <h3 className="text-lg font-bold text-gray-800 mb-4">Help Topics</h3>
            <nav className="space-y-2">
              {Object.entries(helpSections).map(([key, section]) => (
                <button
                  key={key}
                  onClick={() => setActiveSection(key)}
                  className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                    activeSection === key
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <span className="mr-2">{section.icon}</span>
                  {section.title}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
            {searchTerm ? (
              <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-6">
                  Search Results for "{searchTerm}"
                </h2>
                <div className="space-y-6">
                  {filteredSections.map(([key, section]) => (
                    <div key={key}>
                      <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                        <span className="mr-2">{section.icon}</span>
                        {section.title}
                      </h3>
                      <div className="space-y-4">
                        {section.content
                          .filter(item => 
                            item.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            item.answer.toLowerCase().includes(searchTerm.toLowerCase())
                          )
                          .map((item, index) => (
                            <div key={index} className="border-l-4 border-indigo-500 pl-4">
                              <h4 className="font-medium text-gray-800 mb-2">{item.question}</h4>
                              <p className="text-gray-600">{item.answer}</p>
                            </div>
                          ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                  <span className="mr-3">{helpSections[activeSection].icon}</span>
                  {helpSections[activeSection].title}
                </h2>
                
                <div className="space-y-6">
                  {helpSections[activeSection].content.map((item, index) => (
                    <div key={index} className="border-l-4 border-indigo-500 pl-4">
                      <h3 className="font-medium text-gray-800 mb-2">{item.question}</h3>
                      <p className="text-gray-600">{item.answer}</p>
                    </div>
                  ))}
                </div>

                {/* Role-specific help */}
                {roleSpecificHelp[user?.role] && (
                  <div className="mt-8 pt-8 border-t border-gray-200">
                    <h3 className="text-xl font-semibold text-gray-800 mb-4">
                      {user.role.charAt(0).toUpperCase() + user.role.slice(1)}-Specific Help
                    </h3>
                    <div className="space-y-4">
                      {roleSpecificHelp[user.role].map((item, index) => (
                        <div key={index} className="border-l-4 border-green-500 pl-4">
                          <h4 className="font-medium text-gray-800 mb-2">{item.question}</h4>
                          <p className="text-gray-600">{item.answer}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Contact Support */}
          <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-200">
            <h3 className="text-lg font-bold text-gray-800 mb-4">Still need help?</h3>
            <p className="text-gray-600 mb-4">
              Can't find what you're looking for? Our support team is here to help.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg font-medium transition-colors">
                📧 Contact Support
              </button>
              <button className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg font-medium transition-colors">
                💬 Live Chat
              </button>
              <button className="bg-purple-500 hover:bg-purple-600 text-white px-6 py-2 rounded-lg font-medium transition-colors">
                📞 Call Support
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Help;
