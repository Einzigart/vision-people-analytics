"""
Test settings for the TA Project with Supabase.
This file is used when running tests to work with Supabase limitations.
"""
import os

# Import all settings from the main settings file
from .settings import *

# Override database settings for testing with Supabase
# We'll use the same database but with a test schema
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'options': '-c search_path=test,public'
        },
        'TEST': {
            'NAME': None,  # Use the same database
            'CREATE_DB': False,  # Don't create a new database
            'CREATE_SCHEMA': True,  # Create a new schema for tests
        }
    }
}

# Disable migrations during testing for faster test runs
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Use an in-memory cache for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Reduce password validation for testing
AUTH_PASSWORD_VALIDATORS = []

# Use our custom test runner to handle Supabase connection issues
TEST_RUNNER = 'core.test_runner.SupabaseTestRunner'