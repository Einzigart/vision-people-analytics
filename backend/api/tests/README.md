# Backend Tests

This directory contains all the backend tests for the TA Project, organized by functionality.

## Test Organization

- `test_api_endpoints.py` - Tests for the main API endpoints
- `test_age_gender_endpoints.py` - Tests for age/gender specific endpoints
- `test_aggregation.py` - Tests for the data aggregation functionality
- `test_consolidated_endpoints.py` - Tests for the consolidated statistics endpoints
- `test_export_functionality.py` - Tests for the data export functionality
- `test_views.py` - Unit tests for API views

## Running Tests

To run all tests:

```bash
python -m pytest
```

To run a specific test file:

```bash
python -m pytest api/tests/test_api_endpoints.py
```

To run tests with coverage:

```bash
python -m pytest --cov=api
```