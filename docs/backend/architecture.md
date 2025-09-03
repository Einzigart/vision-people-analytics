# Backend Architecture Documentation

## Overview

The backend of the Visitor Counter Web Interface is built using Django 5.0 with Django REST Framework. It provides a robust API for handling people counting data, demographic analysis, and system management.

## Folder Structure

```
backend/
├── api/                    # Main application
│   ├── models.py          # Database models
│   ├── views.py           # API endpoints
│   ├── serializers.py     # Data serialization
│   ├── services.py        # Business logic
│   ├── signals.py         # Event handlers
│   ├── cache_service.py   # Redis caching
│   ├── performance_utils.py # Performance monitoring
│   ├── management/        # Custom commands
│   │   └── commands/      # Django management commands
│   └── tests/             # Unit and integration tests
├── core/                  # Project settings
│   ├── settings.py        # Main configuration
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI entry point
├── requirements.txt       # Python dependencies
├── manage.py             # Django management script
└── README.md             # Backend-specific documentation
```

## Key Components

### 1. Models (`api/models.py`)

#### DetectionData
Stores raw detection data from YOLO model per minute, including detailed age and gender demographics:
- `timestamp`: DateTime with index
- Male age groups (0-9, 10-19, 20-29, 30-39, 40-49, 50+)
- Female age groups (0-9, 10-19, 20-29, 30-39, 40-49, 50+)
- `is_aggregated`: Boolean flag indicating if data has been processed

#### DailyAggregation
Stores daily aggregated data for historical analysis:
- `date`: Date (unique)
- Male age groups
- Female age groups

#### MonthlyAggregation
Stores monthly aggregated data for long-term analysis:
- `year`: Integer
- `month`: Integer
- Male age groups
- Female age groups

#### ModelSettings
Stores configuration settings for the detection model:
- `confidence_threshold_person`: Float (0.0-1.0)
- `confidence_threshold_face`: Float (0.0-1.0)
- `log_interval_seconds`: Integer
- `last_updated`: DateTime
- `updated_by`: Foreign key to User

### 2. Views (`api/views.py`)

#### API Endpoints
- Authentication endpoints
- Detection data management
- Analytics and statistics
- System configuration
- Health and performance monitoring

#### Key Functions
- `api_overview`: Provides API documentation endpoint
- `today_stats`: Returns today's comprehensive statistics
- `range_stats`: Returns statistics for a date range
- `daily_aggregations`: Returns daily aggregated data
- `monthly_aggregations`: Returns monthly aggregated data
- `detection_data`: Handles detection data submission and retrieval
- `model_settings`: Manages model configuration
- `trigger_aggregation`: Manually triggers data aggregation
- `health_check`: Returns system health status
- `performance_stats`: Returns performance metrics

### 3. Services (`api/services.py`)

#### StatsService
Handles statistical calculations and data processing:
- `get_today_stats`: Calculates today's statistics
- `get_range_stats`: Calculates statistics for a date range
- `get_daily_aggregations`: Retrieves daily aggregated data
- `get_monthly_aggregations`: Retrieves monthly aggregated data

#### AggregationService
Manages data aggregation processes:
- `run_aggregation`: Runs the aggregation process
- `aggregate_detection_data`: Aggregates raw detection data
- `create_daily_aggregation`: Creates daily aggregation records
- `create_monthly_aggregation`: Creates monthly aggregation records

#### DateRangeService
Handles date range calculations and validation:
- `validate_date_range`: Validates date range inputs
- `get_date_range`: Generates date ranges for queries

### 4. Serializers (`api/serializers.py`)

#### DetectionDataSerializer
Serializes detection data for API responses:
- Handles both input and output serialization
- Includes validation for required fields

#### DailyAggregationSerializer
Serializes daily aggregation data:
- Formats data for chart visualization
- Includes computed properties

#### MonthlyAggregationSerializer
Serializes monthly aggregation data:
- Formats data for long-term analysis
- Includes computed properties

#### ModelSettingsSerializer
Serializes model settings:
- Handles configuration updates
- Includes validation for threshold values

### 5. Signals (`api/signals.py`)

#### post_save signal for DetectionData
Triggers aggregation processes when new detection data is saved:
- Updates aggregation flags
- Schedules aggregation tasks

## Environment Variables

### Core Settings
```bash
# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
SECRET_KEY=your-secret-key-here
DEBUG=True  # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Redis Caching (optional)
REDIS_URL=redis://localhost:6379/0
ENABLE_CACHING=True

# Security
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

### Development Settings
```bash
# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/backend.log

# Performance
CACHE_TIMEOUT=300  # 5 minutes
```

## Dependencies

### Core Dependencies
- Django>=5.0.0
- djangorestframework>=3.14.0
- django-cors-headers>=4.3.0
- psycopg2-binary>=2.9.9
- python-dateutil>=2.8.2
- gunicorn>=21.2.0
- whitenoise>=6.5.0
- dj-database-url>=2.1.0
- python-dotenv>=0.21.0
- requests>=2.20.0

### Development Dependencies
- ruff>=0.1.0 (Code quality)
- pytest>=7.0.0 (Testing)
- pytest-django>=4.0.0 (Django testing)

## Database Schema

### DetectionData Table
```sql
CREATE TABLE api_detectiondata (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    male_0_9 INTEGER DEFAULT 0,
    male_10_19 INTEGER DEFAULT 0,
    male_20_29 INTEGER DEFAULT 0,
    male_30_39 INTEGER DEFAULT 0,
    male_40_49 INTEGER DEFAULT 0,
    male_50_plus INTEGER DEFAULT 0,
    female_0_9 INTEGER DEFAULT 0,
    female_10_19 INTEGER DEFAULT 0,
    female_20_29 INTEGER DEFAULT 0,
    female_30_39 INTEGER DEFAULT 0,
    female_40_49 INTEGER DEFAULT 0,
    female_50_plus INTEGER DEFAULT 0,
    is_aggregated BOOLEAN DEFAULT FALSE
);
```

### DailyAggregation Table
```sql
CREATE TABLE api_dailyaggregation (
    id BIGSERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    male_0_9 INTEGER DEFAULT 0,
    male_10_19 INTEGER DEFAULT 0,
    male_20_29 INTEGER DEFAULT 0,
    male_30_39 INTEGER DEFAULT 0,
    male_40_49 INTEGER DEFAULT 0,
    male_50_plus INTEGER DEFAULT 0,
    female_0_9 INTEGER DEFAULT 0,
    female_10_19 INTEGER DEFAULT 0,
    female_20_29 INTEGER DEFAULT 0,
    female_30_39 INTEGER DEFAULT 0,
    female_40_49 INTEGER DEFAULT 0,
    female_50_plus INTEGER DEFAULT 0
);
```

### MonthlyAggregation Table
```sql
CREATE TABLE api_monthlyaggregation (
    id BIGSERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    male_0_9 INTEGER DEFAULT 0,
    male_10_19 INTEGER DEFAULT 0,
    male_20_29 INTEGER DEFAULT 0,
    male_30_39 INTEGER DEFAULT 0,
    male_40_49 INTEGER DEFAULT 0,
    male_50_plus INTEGER DEFAULT 0,
    female_0_9 INTEGER DEFAULT 0,
    female_10_19 INTEGER DEFAULT 0,
    female_20_29 INTEGER DEFAULT 0,
    female_30_39 INTEGER DEFAULT 0,
    female_40_49 INTEGER DEFAULT 0,
    female_50_plus INTEGER DEFAULT 0,
    UNIQUE (year, month)
);
```

### ModelSettings Table
```sql
CREATE TABLE api_modelsettings (
    id BIGSERIAL PRIMARY KEY,
    confidence_threshold_person DOUBLE PRECISION DEFAULT 0.5,
    confidence_threshold_face DOUBLE PRECISION DEFAULT 0.5,
    log_interval_seconds INTEGER DEFAULT 60,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    updated_by_id INTEGER REFERENCES auth_user(id) NULL
);
```

## Database Setup Instructions

### 1. Create Database
```sql
CREATE DATABASE people_counter;
CREATE USER people_counter_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE people_counter TO people_counter_user;
```

### 2. Run Migrations
```bash
cd backend
python manage.py migrate
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
```

### 4. Load Initial Data (Optional)
```bash
python manage.py shell < ../sql_scripts/02_sample_data.sql
```

## Performance Considerations

### Indexing
- Timestamp index on DetectionData for time-based queries
- Date index on DailyAggregation for date-based queries
- Composite index on MonthlyAggregation for year/month queries

### Caching
- Redis caching for frequently accessed data
- Configurable cache timeouts
- Automatic cache invalidation on data updates

### Query Optimization
- Use of select_related and prefetch_related for efficient queries
- Database-level aggregation for performance
- Pagination for large result sets