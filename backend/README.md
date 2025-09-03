# Backend Development Guide

## Project Structure

- `api/` - Main API application
- `api/tests/` - All backend tests, organized by functionality
- `core/` - Django project settings
- `scripts/` - Utility scripts for development and maintenance
- `logs/` - Application logs

## Code Quality

We use Ruff for linting and code formatting. To check for errors:

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate.bat

# Run Ruff to check for errors
ruff check .

# Run Ruff to automatically fix issues (where possible)
ruff check --fix .

# Format code
ruff format .
```

## Django Standalone Scripts

When creating standalone Django scripts (scripts that need to interact with Django models outside of the web application), follow this pattern to avoid import order issues:

```python
#!/usr/bin/env python
import os
import sys
import django

def setup_django():
    """Set up Django environment."""
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

def get_models():
    """Import and return Django models."""
    from api.models import MyModel
    return MyModel

def main():
    setup_django()
    MyModel = get_models()
    # Use models here...

if __name__ == '__main__':
    main()
```

This pattern ensures:
1. All imports are at the top of their respective functions (satisfying PEP 8)
2. Django is properly configured before importing models
3. Ruff won't complain about import order (E402 errors)

## Testing

Run tests with:

```bash
python -m pytest
```

Tests are organized in the `api/tests/` directory, with each file focusing on a specific functionality.

## Utility Scripts

Development and maintenance utility scripts are located in the `scripts/` directory. See `scripts/README.md` for details.