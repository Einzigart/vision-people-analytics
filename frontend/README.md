# Visitor Counter Web Interface - Modern Frontend

A modern, responsive React TypeScript dashboard for the Visitor Counter system built with shadcn/ui components and Tailwind CSS.

## Features

### Modern UI/UX
- **shadcn/ui Components**: Beautiful, accessible components built on Radix UI
- **Dark/Light Theme**: System-aware theme switching with manual override
- **Responsive Design**: Mobile-first approach with responsive layouts
- **Professional Styling**: Clean, modern interface with Tailwind CSS

### Dashboard & Analytics
- **Real-time Stats**: Live people counting data with auto-refresh
- **Interactive Charts**: Recharts-powered visualizations
  - Hourly traffic patterns (Bar charts)
  - Gender distribution (Pie charts)
  - Time-series data visualization
- **Statistics Cards**: Key metrics with visual indicators

### Authentication & Security
- **JWT Authentication**: Secure token-based authentication
- **Protected Routes**: Route-level access control
- **Auto Token Refresh**: Seamless session management
- **Form Validation**: Client-side validation with error handling

### Technical Excellence
- **TypeScript**: Full type safety and IntelliSense
- **Context API**: Centralized state management
- **Custom Hooks**: Reusable logic components
- **Error Boundaries**: Graceful error handling
- **Loading States**: Skeleton loading and smooth transitions

## Tech Stack

### Core Framework
- **React 19**: Latest React with concurrent features
- **TypeScript**: Static typing for better DX
- **React Router v7**: Modern routing solution

### UI & Styling
- **shadcn/ui**: High-quality component library
- **Tailwind CSS**: Utility-first CSS framework
- **Radix UI**: Headless UI primitives
- **Lucide React**: Beautiful icon library

### Data Visualization
- **Recharts**: React charting library
- **Custom Chart Components**: Reusable chart implementations

### Development
- **Vite**: Fast dev server and bundler
- **Vitest**: Unit testing framework
- **ESLint & Prettier**: Code quality and formatting
- **PostCSS**: CSS processing

## Quick Start

### Prerequisites
- Node.js 18+
- npm
- Backend API running on port 8000

### Installation

1. **Clone and navigate to frontend**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file (Vite)
   echo "VITE_API_URL=http://localhost:8000/api" > .env
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open browser**
   ```
   http://localhost:3000
   ```

### Build for Production (Vite)
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── ui/           # shadcn/ui components
│   │   ├── charts/       # Chart components
│   │   ├── dashboard/    # Dashboard-specific components
│   │   └── layout/       # Layout components
│   ├── contexts/         # React contexts
│   │   ├── auth-context.tsx
│   │   └── theme-context.tsx
│   ├── pages/            # Page components
│   │   ├── dashboard.tsx
│   │   └── login.tsx
│   ├── services/         # API services
│   │   └── api.ts
│   ├── lib/              # Utilities
│   │   └── utils.ts
│   ├── App.tsx           # Main app component
│   └── index.tsx         # App entry point
├── tailwind.config.js    # Tailwind configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies
```

## Component Library

### UI Components
- **Button**: Multiple variants and sizes
- **Card**: Container component with header/content/footer
- **Badge**: Status indicators with color variants
- **Select**: Dropdown component with search
- **Switch**: Toggle component for settings
- **Skeleton**: Loading placeholders

### Chart Components
- **PeopleCountChart**: Bar chart for temporal data
- **GenderDistributionChart**: Pie chart for demographics

### Layout Components
- **Navbar**: Responsive navigation with theme toggle
- **StatsCard**: Metric display cards with trends

## Configuration

### Environment Variables
```env
VITE_API_URL=http://localhost:8000/api
```

### Theme Configuration
The app supports system, light, and dark themes. Theme preference is stored in localStorage.

### API Configuration
The API service automatically handles:
- JWT token management
- Request/response interceptors
- Error handling
- Token refresh logic

## Data Flow

1. **Authentication Flow**
   ```
   Login → JWT Tokens → Protected Routes → API Calls
   ```

2. **Dashboard Data Flow**
   ```
   Dashboard → API Service → Context/State → Components → Charts
   ```

3. **Theme Flow**
   ```
   Theme Toggle → Context → CSS Variables → Component Styles
   ```

## Key Features

### Dashboard
- **Real-time Updates**: Auto-refresh every minute
- **Responsive Stats**: Mobile-optimized stat cards
- **Interactive Charts**: Hover tooltips and legends
- **Status Indicators**: System health and activity

### Authentication
- **Secure Login**: Form validation and error handling
- **Demo Credentials**: Built-in demo access
- **Auto Logout**: Session management
- **Protected Routes**: Access control

### Charts & Analytics
- **Hourly Traffic**: Time-based people counting
- **Gender Distribution**: Demographic breakdown
- **Custom Theming**: Dark/light mode support
- **Responsive Design**: Mobile-friendly charts

## Development

### Linting
- Config: `eslint.config.mjs` (ESLint flat config for React + TypeScript + Vitest)
- Run: `npm run lint` to check; `npm run lint:fix` to auto-fix
- Scope: ignores `dist/` and `node_modules/`; recognizes Vitest globals in `*.test.tsx`
- Key rules: React Hooks, TypeScript `no-unused-vars` (prefix unused args with `_`)

### Available Scripts
```bash
npm run dev       # Vite development server
npm run build     # Production build (Vite)
npm run preview   # Preview built app locally
npm test          # Run unit tests (Vitest)
npm run lint      # Lint source files
```

### Code Quality
- **TypeScript**: Strict type checking
- **ESLint**: Code linting
- **Prettier**: Code formatting
- **Path Mapping**: Clean imports with @/ alias

### Custom Hooks
- **useAuth**: Authentication state management
- **useTheme**: Theme switching logic
- **useRequireAuth**: Protected route logic

## Deployment

### Development
```bash
npm start
```

### Production Build
```bash
npm run build
npm install -g serve
serve -s build
```

### Environment Setup
1. Configure API endpoint
2. Set up authentication
3. Test all features
4. Deploy to hosting platform

## API Integration

The frontend integrates with the Django REST API:

### Endpoints Used
- `POST /token/` - Authentication
- `GET /dashboard/today/` - Today's statistics
- `GET /analytics/` - Historical data
- `GET /settings/model/` - Model configuration

### Authentication
- JWT token-based authentication
- Automatic token refresh
- Secure logout with token invalidation

## Design System

### Colors
- **Primary**: Blue (customizable)
- **Secondary**: Gray variants
- **Success**: Green
- **Warning**: Yellow
- **Destructive**: Red

### Typography
- **Headings**: Font weights 600-700
- **Body**: Regular weight
- **Captions**: Muted foreground

### Spacing
- **Consistent**: 4px base unit
- **Responsive**: Mobile-first approach
- **Grid**: CSS Grid and Flexbox

## Mobile Support

- **Responsive Navigation**: Collapsible menu
- **Touch-friendly**: Proper touch targets
- **Mobile Charts**: Optimized chart rendering
- **Progressive Enhancement**: Works on all devices

## Browser Support

- **Modern Browsers**: Chrome, Firefox, Safari, Edge
- **ES6+ Features**: Uses modern JavaScript
- **CSS Grid**: Modern layout techniques
- **Responsive**: All screen sizes

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests if needed
5. Submit pull request

## License

This project is part of the YOLO People Counter system.

---

**Built with ❤️ using React, TypeScript, and shadcn/ui**
