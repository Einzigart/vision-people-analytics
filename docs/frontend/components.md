# Frontend Documentation

## Overview

The frontend of the Visitor Counter Web Interface is built using React 19 with TypeScript, providing a responsive and interactive dashboard for visualizing people counting data and demographic analysis.

## Framework and Libraries

### Core Framework
- **React 19**: UI library for building interactive user interfaces
- **TypeScript**: Type safety for better code quality and developer experience
- **React Router**: Client-side routing for navigation

### UI Components
- **Tailwind CSS**: Utility-first CSS framework for styling
- **shadcn/ui**: Reusable component library built on Tailwind CSS
- **Recharts**: Declarative charting library for data visualization
- **Lucide React**: Icon library for UI elements

### State Management
- **React Context API**: Built-in state management solution
- **Custom Hooks**: Reusable logic encapsulation

### Data Handling
- **Axios**: HTTP client for API requests
- **date-fns**: Modern date utility library
- **html2canvas-pro**: Chart export functionality

### Development Tools
- **Vite**: Dev server and bundling
- **Vitest**: Unit testing
- **ESLint**: Code linting
- **Prettier**: Code formatting

## Folder Structure (Vite)

```
frontend/
├── index.html            # Vite HTML entry
├── public/               # Static assets (copied as-is)
├── src/                  # Source code
│   ├── components/       # Reusable UI components
│   │   ├── ui/           # shadcn/ui components
│   │   ├── charts/       # Chart components
│   │   ├── dashboard/    # Dashboard-specific components
│   │   ├── analytics/    # Analytics-specific components
│   │   ├── common/       # Common/shared components
│   │   └── layout/       # Layout components
│   ├── pages/            # Page components (dashboard, analytics, login, settings)
│   ├── services/         # API integration (api.ts, export-service.ts)
│   ├── contexts/         # React contexts (auth-context.tsx, theme-context.tsx)
│   ├── lib/              # Utilities (utils.ts, chart-colors.ts)
│   ├── App.tsx           # Main application component
│   ├── index.tsx         # App entry point
│   ├── index.css         # Global styles
│   └── setupTests.ts     # Test setup (Vitest/JSDOM)
├── tailwind.config.js    # Tailwind configuration
├── tsconfig.json         # TypeScript configuration
├── vite.config.mts       # Vite configuration
├── .env                  # Environment variables (VITE_*)
├── package.json          # Dependencies and scripts
└── README.md             # Frontend-specific documentation
```

## Component Hierarchy

### Main Application Structure
```
App
├── AuthProvider
│   └── ThemeProvider
│       └── Router
│           ├── Login
│           ├── Dashboard
│           ├── Analytics
│           ├── Settings
│           └── NotFound
```

### Dashboard Page
```
Dashboard
├── Header
├── StatsGrid
│   ├── StatsCard (Total People)
│   ├── StatsCard (Male Count)
│   ├── StatsCard (Female Count)
│   └── StatsCard (Data Points)
├── PeopleCountChart
├── GenderDistributionChart
├── AgeDistributionChart
└── RecentActivity
```

### Analytics Page
```
Analytics
├── DateRangePicker
├── NavigationTabs
├── StatsGrid
├── PeopleCountSection
├── GenderDistributionSection
├── EnhancedGenderDemographics
├── AgeDistributionSection
└── ExportMenu
```

## State Management

### Authentication Context
The `AuthContext` manages user authentication state throughout the application:
- `user`: Current authenticated user
- `isAuthenticated`: Authentication status
- `login()`: Authenticate user
- `logout()`: End user session

### Theme Context
The `ThemeContext` manages the application's color scheme:
- `theme`: Current theme ('light' or 'dark')
- `toggleTheme()`: Switch between themes
- `setTheme()`: Set specific theme

## Major UI Components

### Dashboard Components

#### StatsCard
Displays a key metric with icon and description.

**Props**:
```typescript
interface StatsCardProps {
  title: string;
  value: number;
  icon: React.ComponentType<{ className?: string }>;
  variant?: 'default' | 'success' | 'warning' | 'destructive';
  description?: string;
}
```

#### PeopleCountChart
Interactive chart showing people count over time.

**Props**:
```typescript
interface PeopleCountChartProps {
  data: Record<string, { male: number; female: number; total: number }>;
  type: 'hourly' | 'daily' | 'weekly' | 'monthly';
}
```

#### GenderDistributionChart
Pie chart showing gender distribution.

**Props**:
```typescript
interface GenderDistributionChartProps {
  male: number;
  female: number;
}
```

### Analytics Components

#### DateRangePicker
Component for selecting date ranges with preset options.

**Props**:
```typescript
interface DateRangePickerProps {
  onDateRangeChange: (startDate: Date, endDate: Date) => void;
  initialStartDate: Date;
  initialEndDate: Date;
  serverReferenceDate: Date | null;
}
```

#### ExportMenu
Dropdown menu for exporting data in various formats.

**Props**:
```typescript
interface ExportMenuProps {
  exporting: boolean;
  exportingType: string;
  showExportMenu: boolean;
  setShowExportMenu: (show: boolean) => void;
  handleExportAction: (action: string) => void;
}
```

### Common Components

#### Card
Reusable card component with header and content sections.

**Props**:
```typescript
interface CardProps {
  children: React.ReactNode;
  className?: string;
}
```

#### Button
Customizable button component with variants.

**Props**:
```typescript
interface ButtonProps {
  children: React.ReactNode;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg';
  onClick?: () => void;
  disabled?: boolean;
}
```

## API Integration

### API Service (`services/api.ts`)
Centralized API client handling authentication and error management.

#### Key Functions:
- `getTodayStats()`: Fetch today's statistics
- `getRangeStats(start, end)`: Fetch statistics for date range
- `getDailyAggregations()`: Fetch daily aggregated data
- `getMonthlyAggregations()`: Fetch monthly aggregated data
- `getModelSettings()`: Fetch model settings
- `updateModelSettings()`: Update model settings
- `triggerAggregation()`: Manually trigger data aggregation
- `login(username, password)`: Authenticate user
- `logout()`: End user session

### Export Service (`services/export-service.ts`)
Handles data export functionality for charts and reports.

#### Key Functions:
- `exportDataAsCSV(data, dateRange)`: Export data as CSV
- `exportDataAsPDF(rangeStats, dateRange, totals, chartRefs)`: Export data as PDF
- `exportChartsAsPNG(chartRefs, dateRange)`: Export charts as PNG images
- `exportAgeGenderDataAsCSV(data, dateRange)`: Export age/gender data as CSV

## Environment Variables

### Required Variables
```bash
# API Base URL
REACT_APP_API_URL=http://localhost:8000/api

# Feature Flags
REACT_APP_ENABLE_DARK_MODE=true
REACT_APP_DEFAULT_DATE_RANGE=7
```

### Optional Variables
```bash
# Analytics
REACT_APP_ANALYTICS_ID=your-analytics-id

# Performance
REACT_APP_POLLING_INTERVAL=60000  # 60 seconds
```

## Build and Setup Instructions

### Prerequisites
- Node.js 16+ with npm
- Access to backend API

### Development Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file:**
   ```bash
   echo "REACT_APP_API_URL=http://localhost:8000/api" > .env
   ```

4. **Start development server:**
   ```bash
   npm start
   ```

5. **Access the application:**
   Open http://localhost:3000 in your browser

### Production Build

1. **Create production build:**
   ```bash
   npm run build
   ```

2. **Serve build files:**
   The build files will be in the `build/` directory and can be served by any static file server.

### Testing

1. **Run unit tests:**
   ```bash
   npm test
   ```

2. **Run tests with coverage:**
   ```bash
   npm test -- --coverage
   ```

3. **Lint code:**
   ```bash
   npm run lint
   ```

4. **Fix linting issues:**
   ```bash
   npm run lint:fix
   ```

## Deployment

### Netlify Deployment

1. **Connect GitHub repository** to Netlify
2. **Configure build settings:**
   ```
   Build command: npm run build
   Publish directory: build
   ```
3. **Set environment variables:**
   ```
   REACT_APP_API_URL=https://your-backend-domain.com/api
   ```

### Vercel Deployment

1. **Import project** from GitHub
2. **Configure build settings** (auto-detected)
3. **Set environment variables** in dashboard

### Custom Server Deployment

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Serve build directory** with your preferred web server (Nginx, Apache, etc.)

3. **Configure reverse proxy** to backend API if needed

## Performance Considerations

### Bundle Optimization
- Code splitting for lazy-loaded components
- Tree shaking for unused code elimination
- Minification for production builds

### Data Fetching
- Caching of API responses
- Pagination for large datasets
- Loading states for better UX

### Rendering
- Virtualized lists for large data sets
- Memoization of expensive calculations
- Conditional rendering to avoid unnecessary updates

## Responsive Design

### Breakpoints
- `sm`: 640px (small screens)
- `md`: 768px (medium screens)
- `lg`: 1024px (large screens)
- `xl`: 1280px (extra large screens)
- `2xl`: 1536px (2x extra large screens)

### Mobile-First Approach
- Base styles for mobile devices
- Progressive enhancement for larger screens
- Touch-friendly controls and interactions

## Accessibility

### ARIA Labels
- Proper labeling of interactive elements
- Descriptive alt text for images
- Semantic HTML structure

### Keyboard Navigation
- Full keyboard support for all interactive elements
- Focus management for modals and dialogs
- Skip links for screen readers

### Color Contrast
- WCAG 2.1 AA compliant color contrast
- Dark/light mode with appropriate contrast ratios
- Focus indicators for interactive elements

## Customization

### Theme Customization
- Tailwind CSS configuration in `tailwind.config.js`
- Custom color schemes in `src/styles/globals.css`
- Component variants in `src/components/ui/`

### Branding
- Logo replacement in `public/` directory
- Color scheme updates in theme configuration
- Typography customization in global styles

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check `REACT_APP_API_URL` in `.env` file
   - Verify backend server is running
   - Check CORS configuration

2. **Build Failures**
   - Clear node_modules and reinstall dependencies
   - Check TypeScript errors
   - Verify environment variables

3. **Performance Issues**
   - Check browser console for errors
   - Monitor network requests
   - Profile component rendering

### Debugging Tools

1. **React DevTools**: Component hierarchy inspection
2. **Redux DevTools**: State management debugging (if used)
3. **Browser DevTools**: Network, performance, and console debugging
4. **TypeScript Compiler**: Type checking and error reporting

## Contributing

### Development Workflow

1. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "Add your feature"
   ```

3. **Push and create pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Standards

1. **TypeScript**: Use strong typing for all components and functions
2. **ESLint**: Follow configured linting rules
3. **Prettier**: Maintain consistent code formatting
4. **Component Structure**: Follow established patterns for new components
5. **Testing**: Add unit tests for new functionality

### Component Development

1. **Create component file** in appropriate directory
2. **Define TypeScript interfaces** for props
3. **Implement component logic** with proper error handling
4. **Add storybook stories** for component documentation
5. **Write unit tests** for component functionality
