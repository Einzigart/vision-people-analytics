# Visitor Counter Web Interface with Computer Vision

A comprehensive web interface for an AI-powered people counting and demographic analysis system based on object detection algorithms with age and gender classification.

## Project Overview
![alt text](image.png)
This project provides a complete solution for real-time people counting and demographic analysis using computer vision. The system integrates various object detection models with a modern web interface to visualize real-time and historical data, providing insights on people count and demographic distribution.

### Key Value Proposition
- **Real-time Analytics**: Continuous monitoring with minute-by-minute data collection
- **Demographic Insights**: Detailed age and gender classification (6 age groups: 0-9, 10-19, 20-29, 30-39, 40-49, 50+)
- **Historical Analysis**: Comprehensive data analysis with customizable date ranges
- **Data Export**: Multiple export formats (CSV, Excel, PDF, PNG) for reporting
- **Responsive Design**: Mobile-first interface that works on all devices
- **System Management**: Real-time configuration of detection parameters

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js 16+** with npm
 - **Node.js 16+** and pnpm (recommended via corepack)
- **Python 3.10+** with pip
- **PostgreSQL 12+** database (or Supabase for cloud deployment)
- **Redis** (optional, for caching)

## Quick Start Guide

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ta-project-web
   ```

2. **Set up the backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

3. **Set up the frontend (Vite):**
   ```bash
   cd frontend
   pnpm install
   echo "VITE_API_URL=http://localhost:8000/api" > .env
   pnpm run dev
   ```

4. **Set up and run the detection model:**
   ```bash
   cd detectionmodel
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   # For live detection with computer vision models, ensure you have PyTorch and OpenCV installed:
   # pip install torch torchvision opencv-python
   python dummytestscript.py  # For testing with dummy data
   # Or run live detection: python live_detection_with_api.py --api-url http://localhost:8000/api
   ```

5. **Access the application:**
   - Frontend (Vite dev): http://localhost:3000
   - Backend API: http://localhost:8000/api
   - Admin Panel: http://localhost:8000/admin

## Docker Setup

This repository now includes Docker support. Added files:
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `detectionmodel/Dockerfile`
- `frontend/nginx.conf`
- `docker-compose.yml`

Quick start (development)
1. Build and run the containers:
    ```bash
    docker-compose up --build
    ```
2. Common URLs:
    * Frontend: http://localhost:3000
    * Backend API: http://localhost:8000
    * Detection Model API: http://localhost:8080

Optional commands
- Build images only:
    ```bash
    docker-compose build
    ```
- Rebuild without cache:
    ```bash
    docker-compose build --no-cache
    docker-compose up -d
    ```
- Stop and remove containers, networks and volumes:
    ```bash
    docker-compose down -v
    ```

Environment files
- Copy and edit example env files if you need to customize:
    ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
    ```
 - The compose configuration is configured to read `backend/.env` and `frontend/.env` via `env_file` entries. Important: Vite (the frontend) reads `VITE_` variables at build time and embeds them into the static bundle — make sure `frontend/.env` exists with `VITE_API_URL` before you run `docker compose build` (or `docker compose up --build`).

Notes
- The frontend container serves the React build behind nginx using `frontend/nginx.conf`.
- The detection model runs in its own service using `detectionmodel/Dockerfile`.
- For production deployments, adjust `docker-compose.yml`, secrets, and `ALLOWED_HOSTS`/security settings appropriately.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────────┐
│   YOLO Model    │───▶│ Django API   │───▶│ PostgreSQL   │───▶│ React Frontend │
│ (Local Device)  │    │ (Backend)    │    │ (Database)   │    │ (Web Interface)│
└─────────────────┘    └──────────────┘    └──────────────┘    └────────────────┘
```

### Backend (Django 5.0)
- RESTful API endpoints for data management and analytics
- PostgreSQL database with optimized indexing
- Automated data aggregation (daily/monthly)
- Redis caching for performance optimization
- JWT-based authentication system

### Frontend (React 19.1 + TypeScript)
- Responsive UI with Tailwind CSS and shadcn/ui components
- Interactive data visualization with Recharts
- Real-time updates with polling mechanism
- Dark/light mode with automatic system detection
- Comprehensive analytics dashboard

### Data Flow
1. YOLO Model processes video input and detects people with gender classification
2. Detection data is sent to Django backend API every minute
3. Data is stored in PostgreSQL and automatically aggregated
4. React frontend fetches and visualizes data in real-time

## Detailed Setup Instructions

### Backend Setup (Django)

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database:**
   Create a PostgreSQL database and update `core/settings.py` with your credentials, or set the `DATABASE_URL` environment variable:
   ```bash
   DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load sample data (optional):**
   ```bash
   python manage.py shell < ../sql_scripts/02_sample_data.sql
   ```

8. **Start development server:**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup (React + TypeScript + Vite)

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   pnpm install
   ```

3. **Create environment file:**
   ```bash
   echo "VITE_API_URL=http://localhost:8000/api" > .env
   ```

4. **Start development server:**
   ```bash
   pnpm run dev
   ```

### Production Deployment

#### Backend Deployment Options

##### Option 1: Railway/Render/Heroku
1. Connect your repository to your chosen platform
2. Set environment variables:
   ```
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-domain.com
   ```
3. Deploy - the platform will automatically run migrations

##### Option 2: VPS/Cloud Server
1. Set up server with Python 3.9+, PostgreSQL, and Nginx
2. Clone repository and install dependencies
3. Configure Gunicorn and Nginx for production
4. Set up SSL with Let's Encrypt

#### Frontend Deployment
You can deploy on you own choice of platforms. Some are follows:

##### Option 1: Netlify (Vite)
1. Connect GitHub repository to Netlify
2. Build settings:
   ```
   Build command: npm run build
   Publish directory: dist
   ```
3. Environment variables:
   ```
   VITE_API_URL=https://your-backend-domain.com/api
   ```

##### Option 2: Vercel
1. Import project from GitHub
2. Configure build settings (auto-detected)
3. Set environment variables in dashboard

## Environment Variables

### Backend (.env or system environment)
```bash
# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Security Settings
SECRET_KEY=your-secret-key-here
DEBUG=True  # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Redis Caching (optional)
REDIS_URL=redis://localhost:6379/0

# Optional Features
ENABLE_CACHING=True
LOG_LEVEL=INFO
```

### Frontend (.env)
```bash
# API Configuration
VITE_API_URL=http://localhost:8000/api

# Feature Flags
VITE_ENABLE_DARK_MODE=true
VITE_DEFAULT_DATE_RANGE=7  # Last 7 days

# Optional Debug/Logging
VITE_DEBUG_MODE=false
VITE_LOG_LEVEL=warn
```

## Project Structure

```
ta-project-web/
├── backend/                    # Django Backend
│   ├── api/                   # Main API application
│   │   ├── models.py          # Database models
│   │   ├── views.py           # API endpoints and business logic
│   │   ├── serializers.py     # Data serialization
│   │   ├── services.py        # Business logic services
│   │   ├── signals.py         # Data aggregation automation
│   │   ├── cache_service.py   # Redis caching layer
│   │   ├── performance_utils.py # Performance monitoring
│   │   └── management/        # Custom Django commands
│   ├── core/                  # Django project settings
│   │   ├── settings.py        # Main configuration
│   │   └── urls.py           # URL routing
│   ├── requirements.txt       # Python dependencies
│   └── manage.py             # Django management script
├── frontend/                  # React Frontend (Vite)
│   ├── index.html            # Vite HTML entry
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API integration
│   │   ├── contexts/          # React contexts
│   │   ├── lib/               # Utility functions
│   │   ├── App.tsx            # Root component
│   │   └── index.tsx          # Entry point
│   ├── package.json          # Node.js dependencies
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   └── vite.config.mts       # Vite configuration
├── detectionmodel/           # ML Model Integration
│   ├── dummytestscript.py   # Simulation script for testing
│   ├── live_detection.py    # Real YOLO integration
│   ├── live_detection_with_api.py  # Complete integration with API communication
│   ├── live_detection_mobilenet.py  # MobileNet-SSD implementation
│   ├── live_detection_shufflenet.py  # ShuffleNet implementation
│   ├── live_detection_efficientnet.py  # EfficientNet implementation
│   ├── live_detection_with_api.py  # Live detection script with API communication
│   ├── weights/              # Pre-trained models
│   │   ├── efficientnet_liteb0_multi_task_best.pth   # EfficientNet Lite model
│   │   ├── shufflenetv2_multi_task_best.pth # ShuffleNet model
│   │   ├── efficientnet_liteb0_multi_task_best.pth # EfficientNet model
│   │   ├── Yolov11n.pt # YOLOv11n person detection model
│   │   └── Yolov11n-face.pt # YOLOv11n face detection model
│   └── README.md            # Model integration guide
├── sql_scripts/             # Database utilities
│   ├── 01_generate_today_data.sql # Generate sample data for today
│   ├── 02_generate_week_data.sql  # Generate sample data for the past week
│   ├── 03_clear_data.sql          # Clear detection data within a date range
│   ├── 04_quick_test_data.sql     # Generate minimal test data
│   ├── 05_flexible_date_range_generator.sql # Generate data for custom date ranges
│   ├── 06_clear_all_data.sql      # Clear all detection data
│   ├── 07_generate_1_year_data.sql # Generate one year of historical data
│   ├── 08_check_aggregation_status.sql # Check the status of data aggregation processes
│   └── README.md                  # Overview and usage instructions
└── docs/                    # Comprehensive documentation
    ├── backend/            # Backend documentation
    ├── api/                # API documentation
    ├── frontend/           # Frontend documentation
    └── README.md           # Documentation index
```

## Object Detection Model Integration

### Data Format
The API expects detection data with detailed age and gender demographics:

```json
{
  "timestamp": "2025-01-23T14:30:00Z",
  "male_0_9": 1,
  "male_10_19": 2,
  "male_20_29": 3,
  "male_30_39": 2,
  "male_40_49": 1,
  "male_50_plus": 0,
  "female_0_9": 0,
  "female_10_19": 1,
  "female_20_29": 2,
  "female_30_39": 3,
  "female_40_49": 1,
  "female_50_plus": 1
}
```

### Python Integration Example
```python
import requests
import json
from datetime import datetime

# Detection data from your YOLO model
detection_data = {
    "timestamp": datetime.now().isoformat(),
    "male_0_9": 1, "male_10_19": 2, "male_20_29": 3,
    "male_30_39": 2, "male_40_49": 1, "male_50_plus": 0,
    "female_0_9": 0, "female_10_19": 1, "female_20_29": 2,
    "female_30_39": 3, "female_40_49": 1, "female_50_plus": 1
}

# Send to API
api_url = "https://your-backend-domain.com/api/detections/"
headers = {"Content-Type": "application/json"}
response = requests.post(api_url, json=detection_data, headers=headers)

if response.status_code == 201:
    print("Data sent successfully!")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

## API Endpoints

### Core Data Endpoints
- **`GET /api/`** - API overview and documentation
- **`POST /api/detections/`** - Submit detection data
- **`GET /api/detections/`** - Retrieve detection logs

### Analytics Endpoints
- **`GET /api/stats/today/`** - Today's comprehensive statistics
- **`GET /api/stats/range/<start>/<end>/`** - Date range analytics
- **`GET /api/daily/`** - Daily aggregated data
- **`GET /api/monthly/`** - Monthly aggregated data

### Authentication
- **`POST /api/auth/login/`** - User authentication
- **`POST /api/auth/logout/`** - User logout

### Configuration
- **`GET/PUT /api/settings/`** - Model settings (authenticated)
- **`GET /api/public-settings/`** - Public model settings

### System Management
- **`POST /api/trigger-aggregation/`** - Manual data aggregation
- **`GET /api/health/`** - System health check
- **`GET /api/performance/`** - Performance metrics

## Testing & Development

### Running Tests
```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm test
```

### Database Management
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py flush

# Run aggregation manually
python manage.py run_aggregation
```

## Documentation

Comprehensive documentation is available in the [docs](docs/) directory:

### Backend
- [Architecture Overview](docs/backend/architecture.md) - System architecture, database schema, and backend components
- [SQL Scripts](docs/backend/sql-scripts.md) - Database management and testing scripts

### API
- [Endpoints Reference](docs/api/endpoints.md) - Complete API reference with examples and usage workflows

### Frontend
- [Components and Structure](docs/frontend/components.md) - React component hierarchy and UI documentation
- [Model Detection](docs/frontend/model-detection.md) - Object detection model integration

See the [Documentation Index](docs/README.md) for a complete overview of all available documentation.

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the diagnostic scripts in `sql_scripts/`
- Open an issue on GitHub with detailed information
