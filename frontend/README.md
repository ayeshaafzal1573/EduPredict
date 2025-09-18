# EduPredict Frontend

## Overview

EduPredict Frontend is a modern React application that provides role-based dashboards and interfaces for the EduPredict AI-powered student performance prediction system. Built with React, TailwindCSS, and modern web technologies.

## Features

### Role-Based Dashboards
- **Student Dashboard**: Performance tracking, predictions, and academic insights
- **Teacher Dashboard**: Class management, grading, and student analytics
- **Admin Dashboard**: User management, system oversight, and institutional analytics
- **Analyst Dashboard**: Advanced analytics, ML model management, and reporting

### Core Functionality
- **Authentication**: Secure login/logout with JWT tokens
- **Real-time Data**: Live updates and notifications
- **Responsive Design**: Mobile-first design that works on all devices
- **Interactive Charts**: Data visualization with Recharts
- **AI Predictions**: Dropout risk and grade predictions
- **Notification Center**: Real-time alerts and updates

## Technology Stack

- **React 18**: Modern React with hooks and functional components
- **TailwindCSS**: Utility-first CSS framework for styling
- **React Router**: Client-side routing and navigation
- **Axios**: HTTP client for API communication
- **Recharts**: Data visualization and charting library
- **React Hot Toast**: Beautiful toast notifications
- **Lucide React**: Modern icon library

## Quick Start

### Prerequisites

- Node.js 16 or higher
- npm or yarn package manager
- EduPredict Backend running on `http://localhost:8000`

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start development server**
   ```bash
   npm start
   ```

The application will be available at `http://localhost:3000`.

## Project Structure

```
frontend/src/
├── components/          # Reusable UI components
│   ├── Charts/         # Chart components
│   ├── Common/         # Common UI elements
│   ├── Dashboard/      # Dashboard-specific components
│   ├── Layout/         # Layout components
│   └── Notifications/  # Notification components
├── contexts/           # React contexts
│   ├── AuthContext.js  # Authentication state
│   └── ThemeContext.js # Theme management
├── pages/              # Page components
│   ├── Auth/          # Authentication pages
│   ├── Student/       # Student role pages
│   ├── Teacher/       # Teacher role pages
│   ├── Admin/         # Admin role pages
│   ├── Analyst/       # Analyst role pages
│   └── Common/        # Shared pages
├── services/          # API services
│   └── api.js         # API client and endpoints
├── App.js             # Main application component
└── index.js           # Application entry point
```

## User Roles & Features

### 🎓 Student Features
- **Dashboard**: Academic overview with GPA, attendance, and risk assessment
- **Performance**: Detailed performance analytics and trends
- **Predictions**: AI-powered dropout risk and grade predictions
- **Attendance**: Personal attendance tracking and insights
- **Courses**: Enrolled courses and academic progress
- **Notifications**: Academic alerts and important updates

### 👨‍🏫 Teacher Features
- **Dashboard**: Class overview and student management
- **Classes**: Student roster and class management
- **Attendance**: Mark and track student attendance
- **Grades**: Grade entry and gradebook management
- **Analytics**: Class performance and student insights
- **Notifications**: Student alerts and system updates

### 👨‍💼 Admin Features
- **Dashboard**: System-wide metrics and institutional overview
- **Users**: User management and role assignment
- **Courses**: Course catalog and enrollment management
- **Analytics**: Institutional analytics and reporting
- **Notifications**: System alerts and administrative updates

### 📊 Analyst Features
- **Dashboard**: Advanced analytics and model performance
- **Models**: ML model management and training
- **Reports**: Custom analytics reports and insights
- **Predictions**: Institution-wide prediction analysis
- **Tableau**: Advanced visualization dashboards
- **Notifications**: Model alerts and system updates

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_APP_NAME=EduPredict
REACT_APP_VERSION=1.0.0
```

### API Configuration

The frontend communicates with the backend API through the `services/api.js` module:

```javascript
// API base configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Automatic token handling
// Automatic error handling and user-friendly messages
// Request/response interceptors for consistent behavior
```

## Authentication Flow

1. **Login**: User enters credentials
2. **Token Storage**: JWT token stored in localStorage
3. **Auto-Refresh**: Token automatically included in API requests
4. **Role Routing**: User redirected to appropriate dashboard
5. **Protected Routes**: Access control based on user role

## State Management

### AuthContext
Manages user authentication state:
- User information and role
- Login/logout functionality
- Token management
- Authentication status

### ThemeContext
Manages application theme:
- Light/dark mode toggle
- Theme persistence
- Consistent styling

## Component Architecture

### Layout Components
- **Layout**: Main application layout with sidebar and header
- **Sidebar**: Role-based navigation menu
- **Header**: User info, notifications, and logout

### Dashboard Components
- **RiskAssessment**: AI-powered risk analysis display
- **PerformanceChart**: Interactive performance visualizations

### Common Components
- **LoadingSpinner**: Consistent loading states
- **ErrorBoundary**: Error handling and recovery
- **Modal**: Reusable modal dialogs

## Data Flow

1. **API Calls**: Components make API calls through service layer
2. **State Updates**: Successful responses update component state
3. **UI Updates**: React re-renders components with new data
4. **Error Handling**: Errors display user-friendly messages
5. **Loading States**: Loading indicators during API calls

## Styling Guidelines

### TailwindCSS Classes
- **Spacing**: Use consistent spacing scale (4, 6, 8, 12, 16, 24)
- **Colors**: Use semantic color names (blue-500, green-600, red-500)
- **Responsive**: Mobile-first responsive design
- **Gradients**: Consistent gradient patterns for visual appeal

### Component Styling
```javascript
// Card component example
<div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-white/20">
  {/* Content */}
</div>

// Button component example
<button className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200">
  Click Me
</button>
```

## Performance Optimization

### Code Splitting
- Route-based code splitting with React.lazy()
- Component-level splitting for large components
- Dynamic imports for heavy libraries

### Caching
- API response caching where appropriate
- Image optimization and lazy loading
- Service worker for offline functionality

### Bundle Optimization
- Tree shaking for unused code elimination
- Minification and compression
- Asset optimization

## Testing

### Unit Tests
```bash
npm test
```

### Integration Tests
```bash
npm run test:integration
```

### E2E Tests
```bash
npm run test:e2e
```

## Build & Deployment

### Development Build
```bash
npm start
```

### Production Build
```bash
npm run build
```

### Docker Deployment
```bash
# Build image
docker build -t edupredict-frontend .

# Run container
docker run -p 3000:3000 edupredict-frontend
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Accessibility

- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support

## Security

- XSS protection through React's built-in sanitization
- CSRF protection via SameSite cookies
- Secure token storage and handling
- Input validation and sanitization

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify backend is running on correct port
   - Check REACT_APP_API_URL in .env
   - Ensure CORS is properly configured

2. **Authentication Issues**
   - Clear localStorage and try again
   - Check token expiration
   - Verify credentials with backend

3. **Build Errors**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Clear npm cache: `npm cache clean --force`
   - Check for dependency conflicts

4. **Performance Issues**
   - Enable React DevTools Profiler
   - Check for unnecessary re-renders
   - Optimize large lists with virtualization

### Debug Mode

Enable debug logging:
```javascript
// In development
localStorage.setItem('debug', 'edupredict:*');
```

## Contributing

1. **Code Style**: Follow ESLint and Prettier configurations
2. **Components**: Create reusable, well-documented components
3. **Testing**: Add tests for new functionality
4. **Documentation**: Update README for new features

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run test suite
- `npm run eject` - Eject from Create React App (not recommended)

## Browser DevTools

### React DevTools
- Install React DevTools extension
- Inspect component hierarchy and props
- Profile performance issues

### Network Tab
- Monitor API calls and responses
- Check for failed requests
- Analyze loading times

## Support

For frontend-specific issues:
- Check browser console for errors
- Verify API connectivity
- Review component props and state
- Check routing configuration

---

**EduPredict Frontend** - Modern Educational Analytics Interface 🎨