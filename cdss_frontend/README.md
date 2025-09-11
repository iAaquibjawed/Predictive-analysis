# CDSS Frontend

Modern React-based frontend for the Clinical Decision Support System (CDSS)

## 🚀 Features

### **Role-Based Dashboard**
- **Admin**: Full system access, user management, system settings
- **Doctor**: Patient management, prescriptions, symptom analysis
- **Pharmacist**: Drug inventory, interactions, demand forecasting
- **Patient**: Personal health data, medication tracking

### **AI-Powered Features**
- **Symptom Analysis**: Clinical NLP-powered symptom assessment
- **Drug Interactions**: Comprehensive drug interaction checking
- **Compliance Monitoring**: IoT-based medication adherence tracking
- **Demand Forecasting**: ML-powered drug demand predictions
- **Treatment Recommendations**: AI-generated clinical guidance

### **Modern UI/UX**
- Responsive design with Tailwind CSS
- Smooth animations with Framer Motion
- Role-based navigation and permissions
- Real-time notifications and alerts
- Interactive charts and data visualization

## 🛠️ Tech Stack

- **Framework**: React 19.1.1
- **Styling**: Tailwind CSS 3.4.1
- **State Management**: Zustand + React Query
- **Routing**: React Router DOM 6.22.1
- **Forms**: React Hook Form 7.50.1
- **Animations**: Framer Motion 11.0.5
- **Charts**: Recharts 2.12.0
- **Icons**: Heroicons + Lucide React
- **HTTP Client**: Axios
- **Notifications**: React Hot Toast

## 📁 Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── Layout/          # Layout components (Sidebar, Header)
│   ├── Dashboard/       # Dashboard-specific components
│   ├── Common/          # Common UI elements
│   └── Forms/           # Form components
├── pages/               # Page components
│   ├── Auth/            # Authentication pages
│   ├── Dashboard/       # Main dashboard
│   ├── Patients/        # Patient management
│   ├── Drugs/           # Drug management
│   ├── Prescriptions/   # Prescription management
│   ├── Analytics/       # Analytics and reporting
│   └── Settings/        # User and system settings
├── contexts/            # React contexts
│   └── AuthContext.js   # Authentication context
├── services/            # API services
│   └── api.js          # API client and endpoints
├── hooks/               # Custom React hooks
├── utils/               # Utility functions
└── styles/              # Global styles and Tailwind config
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- CDSS Backend running on port 3000
- CDSS ML Service running on port 8001

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cdss_frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Configure environment**
   ```bash
   cp env.local .env.local
   # Edit .env.local with your configuration
   ```

4. **Start development server**
   ```bash
   npm start
   # or
   yarn start
   ```

5. **Open your browser**
   Navigate to `http://localhost:3000`

## ⚙️ Configuration

### Environment Variables

Create a `.env.local` file in the root directory:

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:3000
REACT_APP_ML_API_URL=http://localhost:8001
REACT_APP_ML_API_TOKEN=your_ml_api_token_here

# App Configuration
REACT_APP_NAME=CDSS Frontend
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=development

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_DEBUG_MODE=true
REACT_APP_ENABLE_MOCK_DATA=true
```

### Tailwind CSS Configuration

The project uses a custom Tailwind configuration with:
- Healthcare-specific color palette
- Custom component classes
- Responsive breakpoints
- Animation utilities

## 🔐 Authentication

### User Roles & Permissions

- **Admin**: Full system access
- **Doctor**: Patient and prescription management
- **Pharmacist**: Drug and inventory management
- **Patient**: Personal health data access

### Login Credentials (Demo)

```
Admin: admin@cdss.com / password123
Doctor: doctor@cdss.com / password123
Pharmacist: pharmacist@cdss.com / password123
Patient: patient@cdss.com / password123
```

## 📱 Responsive Design

The application is fully responsive with:
- Mobile-first approach
- Collapsible sidebar navigation
- Touch-friendly interfaces
- Optimized layouts for all screen sizes

## 🎨 UI Components

### Design System

- **Colors**: Primary, secondary, success, warning, danger, neutral
- **Typography**: Inter font family with consistent sizing
- **Spacing**: 4px grid system
- **Shadows**: Soft, medium, and strong shadow variants
- **Animations**: Fade, slide, and scale transitions

### Component Library

- **Cards**: Information containers with headers and bodies
- **Buttons**: Primary, secondary, success, warning, danger variants
- **Forms**: Input fields, labels, validation, and error states
- **Tables**: Sortable, filterable data tables
- **Modals**: Overlay dialogs and confirmations
- **Alerts**: Success, warning, error, and info notifications

## 📊 Data Visualization

### Charts & Graphs

- **Line Charts**: Time series data (compliance trends, vital signs)
- **Bar Charts**: Comparative data (drug usage, patient counts)
- **Pie Charts**: Distribution data (diagnosis breakdown)
- **Gauges**: Performance metrics (compliance rates, accuracy scores)

### Real-time Updates

- Live data refresh
- WebSocket integration (planned)
- Push notifications
- Auto-refresh intervals

## 🔌 API Integration

### Backend Services

- **Rails API**: Core application data
- **ML Service**: AI-powered features
- **Real-time Updates**: WebSocket connections
- **File Uploads**: Document and image handling

### Data Flow

1. **Authentication**: JWT token-based auth
2. **API Calls**: Axios with interceptors
3. **State Management**: React Query for server state
4. **Error Handling**: Centralized error management
5. **Caching**: Intelligent data caching

## 🧪 Testing

### Testing Strategy

- **Unit Tests**: Component testing with Jest
- **Integration Tests**: API integration testing
- **E2E Tests**: User workflow testing
- **Visual Regression**: UI consistency testing

### Running Tests

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

## 🚀 Deployment

### Build Process

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

### Deployment Options

- **Static Hosting**: Netlify, Vercel, AWS S3
- **Container**: Docker with Nginx
- **Cloud**: AWS, Azure, Google Cloud
- **CDN**: CloudFlare, AWS CloudFront

### Environment Configuration

```bash
# Production
REACT_APP_API_URL=https://api.cdss.com
REACT_APP_ML_API_URL=https://ml.cdss.com
REACT_APP_ENVIRONMENT=production
REACT_APP_ENABLE_DEBUG_MODE=false
```

## 🔧 Development

### Code Quality

- **ESLint**: Code linting and formatting
- **Prettier**: Code formatting
- **Husky**: Git hooks for quality checks
- **Commitizen**: Conventional commit messages

### Development Workflow

1. **Feature Branch**: Create feature branch from main
2. **Development**: Implement feature with tests
3. **Code Review**: Submit pull request for review
4. **Testing**: Automated and manual testing
5. **Deployment**: Merge to main and deploy

### Available Scripts

```bash
npm start          # Start development server
npm run build      # Build for production
npm run test       # Run test suite
npm run eject      # Eject from Create React App
npm run lint       # Run ESLint
npm run format     # Run Prettier
```

## 📚 Documentation

### API Documentation

- **OpenAPI/Swagger**: Backend API documentation
- **Component Storybook**: UI component documentation
- **Code Comments**: Inline code documentation
- **README Files**: Module-specific documentation

### User Guides

- **Admin Guide**: System administration
- **Doctor Guide**: Clinical workflows
- **Pharmacist Guide**: Inventory management
- **Patient Guide**: Personal health tracking

## 🤝 Contributing

### Contribution Guidelines

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Add** tests for new functionality
5. **Ensure** all tests pass
6. **Submit** a pull request

### Code Standards

- **React**: Functional components with hooks
- **JavaScript**: ES6+ features and best practices
- **CSS**: Tailwind utility classes
- **Testing**: Jest and React Testing Library
- **Documentation**: JSDoc comments

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Documentation**: Inline code documentation
- **Examples**: Demo applications and use cases

### Contact Information

- **Email**: support@cdss.com
- **GitHub**: [CDSS Repository](https://github.com/cdss)
- **Documentation**: [CDSS Docs](https://docs.cdss.com)

## 🗺️ Roadmap

### Upcoming Features

- [ ] **Real-time Collaboration**: Multi-user editing
- [ ] **Advanced Analytics**: Machine learning insights
- [ ] **Mobile App**: React Native application
- [ ] **Voice Interface**: Speech-to-text integration
- [ ] **Offline Support**: Service worker implementation
- [ ] **Multi-language**: Internationalization support

### Performance Improvements

- [ ] **Code Splitting**: Route-based code splitting
- [ ] **Lazy Loading**: Component lazy loading
- [ ] **Caching**: Advanced caching strategies
- [ ] **Bundle Optimization**: Webpack optimization
- [ ] **CDN Integration**: Content delivery optimization

---

**Built with ❤️ for better healthcare outcomes**
