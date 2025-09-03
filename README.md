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

## Tech Stack

### Backend
- **Django 5.0** with Django REST Framework
- **PostgreSQL** database with optimized indexing
- **Redis** caching for performance
- **JWT** authentication

### Frontend
- **React 19** with TypeScript
- **Tailwind CSS** and shadcn/ui components
- **Recharts** for data visualization
- **Vite** for build tooling

### Computer Vision
- **YOLO models** for object detection
- **Multiple backbones**: EfficientNet, MobileNet, ShuffleNet
- **Real-time processing** with age/gender classification

## Prerequisites

- **Node.js 16+** with pnpm
- **Python 3.10+** with pip
- **PostgreSQL 12+** database
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

Quick start with Docker:
```bash
docker-compose up --build
```

Common URLs:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Detection Model API: http://localhost:8080

## Architecture Overview

```
┌─────────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────────┐
│   YOLO Model    │───▶│ Django API   │───▶│ PostgreSQL   │───▶│ React Frontend │
│ (Local Device)  │    │ (Backend)    │    │ (Database)   │    │ (Web Interface)│
└─────────────────┘    └──────────────┘    └──────────────┘    └────────────────┘
```

### Data Flow
1. YOLO Model processes video input and detects people with gender classification
2. Detection data is sent to Django backend API every minute
3. Data is stored in PostgreSQL and automatically aggregated
4. React frontend fetches and visualizes data in real-time

## Documentation

Comprehensive documentation is available in the [docs](docs/) directory:

- **[Backend Documentation](docs/backend/architecture.md)** - Architecture, setup, and database schema
- **[API Documentation](docs/api/endpoints.md)** - Complete API reference with examples
- **[Frontend Documentation](docs/frontend/components.md)** - Components and UI structure
- **[Model Detection](docs/model%20detection/model-detection.md)** - Computer vision integration
- **[SQL Scripts](docs/backend/sql-scripts.md)** - Database management utilities

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
- Check the documentation in the [docs](docs/) directory
- Open an issue on GitHub with detailed information
