# API Documentation

## Overview

The Visitor Counter Web API provides a RESTful interface for managing people counting data, demographic analysis, and system configuration. All endpoints return JSON responses and follow standard HTTP status codes.

## Authentication

Most endpoints require authentication via JWT tokens. To authenticate:

1. POST to `/api/auth/login/` with username and password
2. Use the returned token in the `Authorization` header: `Bearer <token>`

### Public Endpoints (No Authentication Required)
- `GET /api/` - API overview
- `GET /api/public-settings/` - Public model settings
- `POST /api/detections/` - Submit detection data (if configured)

## Base URL

```
http://localhost:8000/api
```

For production deployments, replace with your domain:
```
https://your-backend-domain.com/api
```

## Error Handling

All API responses follow a consistent format:

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "message": "Descriptive message"
}
```

### Error Response
```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "Descriptive error message",
  "details": { ... }  // Optional additional details
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Endpoints

### Authentication Endpoints

#### Login
```
POST /api/auth/login/
```

**Description**: Authenticate user and receive authentication token

**Request Body**:
```json
{
  "username": "admin",
  "password": "your_password"
}
```

**Response**:
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "username": "admin"
}
```

**Error Responses**:
- `400` - Missing credentials: `{"error": "Please provide both username and password"}`
- `401` - Invalid credentials: `{"error": "Invalid credentials"}`

#### Logout
```
POST /api/auth/logout/
```

**Description**: Invalidate user session

**Headers**: 
- `Authorization: Bearer <token>`

**Response**:
```json
{
  "status": "success",
  "message": "Logout successful"
}
```

### Core Data Endpoints

#### Get API Overview
```
GET /api/
```

**Description**: Get API documentation and available endpoints

**Response**:
```json
{
  "Overview": "/api/",
  "Authentication": "/api/auth/login/",
  "Detection Logs": "/api/detections/",
  "Daily Data": "/api/daily/",
  "Monthly Data": "/api/monthly/",
  "Today Stats (Consolidated)": "/api/stats/today/ (use ?include_demographics=true for age/gender)",
  "Date Range Stats (Consolidated)": "/api/stats/range/<start_date>/<end_date>/ (use ?include_demographics=true for age/gender)",
  "Today Stats (Legacy)": "/api/today/",
  "Today Age Gender Stats (Legacy)": "/api/today-age-gender/",
  "Time Range (Legacy)": "/api/range/<str:start_date>/<str:end_date>/",
  "Age Gender Time Range (Legacy)": "/api/age-gender-range/<str:start_date>/<str:end_date>/",
  "Model Settings": "/api/settings/",
  "Public Model Settings": "/api/public-settings/"
}
```

#### Submit Detection Data
```
POST /api/detections/
```

**Description**: Submit new detection data from YOLO model

**Request Body (Age-Gender Format)**:
```json
{
  "timestamp": "2025-01-23T14:30:00Z",
  "detections": {
    "male": {
      "0-9": 1,
      "10-19": 2,
      "20-29": 3,
      "30-39": 2,
      "40-49": 1,
      "50+": 0
    },
    "female": {
      "0-9": 0,
      "10-19": 1,
      "20-29": 2,
      "30-39": 3,
      "40-49": 1,
      "50+": 1
    }
  }
}
```

**Request Body (Simple Format)**:
```json
{
  "timestamp": "2025-01-23T14:30:00Z",
  "detections": {
    "male": 9,
    "female": 8
  }
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": 12345,
    "timestamp": "2025-01-23T14:30:00Z",
    "male_count": 9,
    "female_count": 8,
    "total_count": 17
  },
  "message": "Age-gender data successfully processed into DetectionData"
}
```

**Error Responses**:
- `400` - Invalid data format: `{"status": "error", "code": "INVALID_PAYLOAD_FORMAT", "message": "..."}`
- `400` - Validation error: `{"status": "error", "code": "VALIDATION_ERROR", "message": "..."}`

#### Get Detection Logs
```
GET /api/detections/?page=1&page_size=50&start_date=2025-01-01&end_date=2025-01-31
```

**Description**: Retrieve detection logs with optional pagination and date filtering

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)
- `start_date` (optional): Filter by start date (YYYY-MM-DD)
- `end_date` (optional): Filter by end date (YYYY-MM-DD)

**Response**:
```json
{
  "status": "success",
  "data": {
    "count": 100,
    "next": "/api/detections/?page=2",
    "previous": null,
    "results": [
      {
        "id": 12345,
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
        "female_50_plus": 1,
        "male_count": 9,
        "female_count": 8,
        "total_count": 17
      }
    ]
  },
  "message": "Detection logs retrieved successfully"
}
```

### Analytics Endpoints

#### Get Today's Statistics
```
GET /api/stats/today/
```

**Description**: Get comprehensive statistics for today

**Response**:
```json
{
  "status": "success",
  "data": {
    "date": "2025-01-23",
    "total_people": 127,
    "male_count": 68,
    "female_count": 59,
    "hourly_data": {
      "00": {"male": 0, "female": 0, "total": 0},
      "01": {"male": 2, "female": 1, "total": 3},
      "02": {"male": 3, "female": 2, "total": 5}
    },
    "demographics": {
      "male": {
        "0-9": 5,
        "10-19": 12,
        "20-29": 18,
        "30-39": 15,
        "40-49": 10,
        "50+": 8
      },
      "female": {
        "0-9": 3,
        "10-19": 10,
        "20-29": 15,
        "30-39": 12,
        "40-49": 8,
        "50+": 5
      }
    }
  },
  "message": "Today's statistics retrieved successfully"
}
```

#### Get Date Range Statistics
```
GET /api/stats/range/2025-01-01/2025-01-31/
```

**Description**: Get statistics for a specific date range

**Path Parameters**:
- `start`: Start date (YYYY-MM-DD)
- `end`: End date (YYYY-MM-DD)

**Response**:
```json
{
  "status": "success",
  "data": {
    "start_date": "2025-01-01",
    "end_date": "2025-01-31",
    "total_people": 3245,
    "male_count": 1723,
    "female_count": 1522,
    "daily_data": {
      "2025-01-01": {"male": 45, "female": 38, "total": 83},
      "2025-01-02": {"male": 52, "female": 47, "total": 99}
    },
    "demographics": {
      "male": {
        "0-9": 156,
        "10-19": 342,
        "20-29": 487,
        "30-39": 398,
        "40-49": 245,
        "50+": 95
      },
      "female": {
        "0-9": 134,
        "10-19": 298,
        "20-29": 423,
        "30-39": 345,
        "40-49": 212,
        "50+": 110
      }
    }
  },
  "message": "Range statistics retrieved successfully"
}
```

#### Get Daily Aggregations
```
GET /api/daily/?page=1&page_size=30&year=2025&month=1
```

**Description**: Get daily aggregated data

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)
- `year` (optional): Filter by year
- `month` (optional): Filter by month

**Response**:
```json
{
  "status": "success",
  "data": {
    "count": 31,
    "next": null,
    "previous": null,
    "results": [
      {
        "date": "2025-01-01",
        "male_count": 45,
        "female_count": 38,
        "total_count": 83,
        "demographics": {
          "male": {
            "0-9": 2,
            "10-19": 8,
            "20-29": 12,
            "30-39": 9,
            "40-49": 7,
            "50+": 7
          },
          "female": {
            "0-9": 1,
            "10-19": 6,
            "20-29": 9,
            "30-39": 8,
            "40-49": 6,
            "50+": 8
          }
        }
      }
    ]
  },
  "message": "Daily aggregations retrieved successfully"
}
```

#### Get Monthly Aggregations
```
GET /api/monthly/?page=1&page_size=12&year=2025
```

**Description**: Get monthly aggregated data

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)
- `year` (optional): Filter by year

**Response**:
```json
{
  "status": "success",
  "data": {
    "count": 12,
    "next": null,
    "previous": null,
    "results": [
      {
        "year": 2025,
        "month": 1,
        "male_count": 1345,
        "female_count": 1203,
        "total_count": 2548,
        "demographics": {
          "male": {
            "0-9": 156,
            "10-19": 342,
            "20-29": 487,
            "30-39": 398,
            "40-49": 245,
            "50+": 95
          },
          "female": {
            "0-9": 134,
            "10-19": 298,
            "20-29": 423,
            "30-39": 345,
            "40-49": 212,
            "50+": 110
          }
        }
      }
    ]
  },
  "message": "Monthly aggregations retrieved successfully"
}
```

### Configuration Endpoints

#### Get Model Settings
```
GET /api/settings/
```

**Description**: Get current model settings (requires authentication)

**Headers**: 
- `Authorization: Token <token>`

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "confidence_threshold_person": 0.5,
    "confidence_threshold_face": 0.5,
    "log_interval_seconds": 60,
    "last_updated": "2025-01-23T14:30:00Z"
  },
  "message": "Model settings retrieved successfully"
}
```

#### Update Model Settings
```
PUT /api/settings/
```

**Description**: Update model settings (requires authentication)

**Headers**: 
- `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "confidence_threshold_person": 0.6,
  "confidence_threshold_face": 0.6,
  "log_interval_seconds": 30
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "confidence_threshold_person": 0.6,
    "confidence_threshold_face": 0.6,
    "log_interval_seconds": 30,
    "last_updated": "2025-01-23T15:45:00Z"
  },
  "message": "Model settings updated successfully"
}
```

#### Get Public Model Settings
```
GET /api/public-settings/
```

**Description**: Get public model settings (no authentication required)

**Response**:
```json
{
  "status": "success",
  "data": {
    "confidence_threshold_person": 0.5,
    "confidence_threshold_face": 0.5,
    "log_interval_seconds": 60
  },
  "message": "Public model settings retrieved successfully"
}
```

### System Management Endpoints

#### Trigger Aggregation
```
POST /api/trigger-aggregation/
```

**Description**: Manually trigger data aggregation process (requires authentication)

**Headers**: 
- `Authorization: Bearer <token>`

**Response**:
```json
{
  "status": "success",
  "data": {
    "aggregated_records": 1247,
    "daily_aggregations_created": 3,
    "monthly_aggregations_updated": 1
  },
  "message": "Aggregation process completed successfully"
}
```

#### Health Check
```
GET /api/health/
```

**Description**: Get system health status

**Response**:
```json
{
  "status": "success",
  "data": {
    "database": "healthy",
    "cache": "healthy",
    "api": "healthy",
    "last_check": "2025-01-23T14:30:00Z"
  },
  "message": "System is healthy"
}
```

#### Performance Metrics
```
GET /api/performance/
```

**Description**: Get system performance metrics (requires authentication)

**Headers**: 
- `Authorization: Bearer <token>`

**Response**:
```json
{
  "status": "success",
  "data": {
    "uptime": "12 days, 4:32:15",
    "average_response_time": 45,
    "requests_per_minute": 127,
    "database_queries_per_request": 2.3,
    "cache_hit_rate": 87.5,
    "memory_usage": "245MB",
    "cpu_usage": "12%"
  },
  "message": "Performance metrics retrieved successfully"
}
```

## Usage Workflows

### 1. Basic Data Submission Workflow

1. **Submit detection data** from YOLO model:
   ```bash
   curl -X POST http://localhost:8000/api/detections/ \
        -H "Content-Type: application/json" \
        -d '{"timestamp": "2025-01-23T14:30:00Z", "male_0_9": 1, ...}'
   ```

2. **Verify submission** by retrieving logs:
   ```bash
   curl http://localhost:8000/api/detections/
   ```

### 2. Analytics Workflow

1. **Get today's statistics**:
   ```bash
   curl http://localhost:8000/api/stats/today/
   ```

2. **Get historical data** for a date range:
   ```bash
   curl http://localhost:8000/api/stats/range/2025-01-01/2025-01-31/
   ```

3. **Get aggregated daily data**:
   ```bash
   curl http://localhost:8000/api/daily/?year=2025&month=1
   ```

### 3. System Management Workflow

1. **Authenticate** as admin user:
   ```bash
   curl -X POST http://localhost:8000/api/auth/login/ \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "your_password"}'
   ```

2. **Update model settings**:
   ```bash
   curl -X PUT http://localhost:8000/api/settings/ \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer <your_token>" \
        -d '{"confidence_threshold_person": 0.6}'
   ```

3. **Trigger manual aggregation**:
   ```bash
   curl -X POST http://localhost:8000/api/trigger-aggregation/ \
        -H "Authorization: Bearer <your_token>"
   ```

### 4. Monitoring Workflow

1. **Check system health**:
   ```bash
   curl http://localhost:8000/api/health/
   ```

2. **Get performance metrics** (authenticated):
   ```bash
   curl -H "Authorization: Bearer <your_token>" \
        http://localhost:8000/api/performance/
   ```

## Rate Limiting

The API implements comprehensive rate limiting to protect against abuse and ensure fair usage across all users.

### Rate Limit Tiers

The API enforces different rate limits based on user authentication status:

#### Unauthenticated Users (IP-based)
- **GET requests**: 100 requests per minute
- **POST requests**: 20 requests per minute
- **PUT requests**: 10 requests per minute
- **DELETE requests**: 5 requests per minute

#### Authenticated Users (User-based)
- **GET requests**: 300 requests per minute
- **POST requests**: 100 requests per minute
- **PUT requests**: 50 requests per minute
- **DELETE requests**: 20 requests per minute

#### Admin Users (Elevated Access)
- **GET requests**: 1000 requests per minute
- **POST requests**: 500 requests per minute
- **PUT requests**: 200 requests per minute
- **DELETE requests**: 100 requests per minute

#### Special Endpoints
- **Detection Data Submission** (`/api/detections/`): 500 POST requests per minute (higher limit for data ingestion)

### Rate Limit Headers

All API responses include rate limiting headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642694400
```

- `X-RateLimit-Limit`: Maximum requests allowed in the current window
- `X-RateLimit-Remaining`: Number of requests remaining in the current window
- `X-RateLimit-Reset`: Unix timestamp when the rate limit window resets

### Rate Limit Exceeded Response

When rate limits are exceeded, the API returns a `429 Too Many Requests` response:

```json
{
  "error": "Rate limit exceeded",
  "detail": "Request was throttled. Expected available in 60 seconds.",
  "code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

**Headers included in 429 responses**:
```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1642694460
Retry-After: 60
```

### Excluded Paths

The following paths are excluded from rate limiting:
- `/admin/` - Django admin interface
- `/static/` - Static files
- `/media/` - Media files  
- `/api/health/` - Health check endpoint

### Configuration

Rate limiting can be configured via environment variables:

```bash
# Enable/disable rate limiting
RATELIMIT_ENABLE=True

# Redis URL for distributed rate limiting
REDIS_URL=redis://localhost:6379/1
```

### Best Practices

1. **Monitor rate limit headers** in your client applications
2. **Implement exponential backoff** when receiving 429 responses
3. **Use authentication** to get higher rate limits
4. **Batch requests** when possible to reduce API calls
5. **Cache responses** to minimize redundant requests

### Example Client Implementation

```javascript
class APIClient {
  async makeRequest(url, options = {}) {
    const response = await fetch(url, options);
    
    // Check rate limit headers
    const limit = response.headers.get('X-RateLimit-Limit');
    const remaining = response.headers.get('X-RateLimit-Remaining');
    const reset = response.headers.get('X-RateLimit-Reset');
    
    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After');
      console.warn(`Rate limited. Retry after ${retryAfter} seconds`);
      
      // Implement exponential backoff
      await this.delay(retryAfter * 1000);
      return this.makeRequest(url, options);
    }
    
    // Log remaining requests
    console.log(`Requests remaining: ${remaining}/${limit}`);
    
    return response;
  }
  
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

### Rate Limiting Architecture

The rate limiting system uses:
- **Redis** for distributed rate limiting (with fallback to local cache)
- **User ID** for authenticated users
- **IP address** for unauthenticated users  
- **Sliding window** algorithm for accurate rate limiting
- **Middleware-based** implementation for consistent enforcement

## CORS Policy

The API allows cross-origin requests from configured origins:
- `http://localhost:3000` (development)
- `https://your-frontend-domain.com` (production)

## Versioning

The API follows semantic versioning. Breaking changes will be introduced in new major versions, with the version number included in the URL path when necessary.
