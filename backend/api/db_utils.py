"""
Database utilities for handling connection issues and retries.
Provides robust database operations for the TA Project.
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Optional

from django.conf import settings
from django.db import connection
from django.db.utils import InterfaceError, OperationalError

logger = logging.getLogger(__name__)


def retry_db_operation(max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator to retry database operations on connection failures.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, InterfaceError) as e:
                    last_exception = e
                    logger.warning(
                        f'Database operation failed (attempt {attempt + 1}/'
                        f'{max_attempts}): {e}'
                    )

                    if attempt < max_attempts - 1:
                        # Close the connection to force a new one
                        connection.close()
                        time.sleep(delay)
                    else:
                        logger.error(
                            f'Database operation failed after {max_attempts} '
                            f'attempts: {e}'
                        )
                        raise last_exception
                except Exception as e:
                    # For non-connection errors, don't retry
                    logger.error(f'Non-retryable database error: {e}')
                    raise

            # This should never be reached, but just in case
            raise last_exception

        return wrapper

    return decorator


def check_database_connection() -> bool:
    """
    Check if the database connection is healthy.

    Returns:
        bool: True if connection is healthy, False otherwise
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        return True
    except Exception as e:
        logger.error(f'Database health check failed: {e}')
        return False


def ensure_database_connection():
    """
    Ensure database connection is available, retry if necessary.
    """
    max_attempts = getattr(settings, 'DATABASE_CONNECTION_RETRY_ATTEMPTS', 3)
    delay = getattr(settings, 'DATABASE_CONNECTION_RETRY_DELAY', 1)

    for attempt in range(max_attempts):
        try:
            if check_database_connection():
                return
        except Exception as e:
            logger.warning(f'Database connection attempt {attempt + 1} failed: {e}')

        if attempt < max_attempts - 1:
            connection.close()
            time.sleep(delay)
        else:
            raise OperationalError(
                'Failed to establish database connection after retries'
            )


class DatabaseConnectionMiddleware:
    """
    Middleware to ensure database connection is healthy before processing requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check database connection before processing request
        try:
            ensure_database_connection()
        except OperationalError as e:
            logger.error(f'Database connection failed in middleware: {e}')
            # Let the request continue - Django will handle the error appropriately

        response = self.get_response(request)
        return response


def safe_database_operation(operation_func: Callable, *args, **kwargs) -> Optional[Any]:
    """
    Execute a database operation safely with retry logic.

    Args:
        operation_func: Function to execute
        *args: Arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Result of the operation or None if all retries failed
    """

    @retry_db_operation()
    def _execute():
        return operation_func(*args, **kwargs)

    try:
        return _execute()
    except Exception as e:
        logger.error(f'Database operation failed permanently: {e}')
        return None


def get_database_stats() -> dict:
    """
    Get database connection statistics and health information.

    Returns:
        dict: Database statistics
    """
    stats = {
        'connection_healthy': False,
        'vendor': 'unknown',
        'database_name': 'unknown',
        'host': 'unknown',
        'port': 'unknown',
    }

    try:
        stats['connection_healthy'] = check_database_connection()
        stats['vendor'] = connection.vendor

        db_settings = connection.settings_dict
        stats['database_name'] = db_settings.get('NAME', 'unknown')
        stats['host'] = db_settings.get('HOST', 'unknown')
        stats['port'] = db_settings.get('PORT', 'unknown')

        # Get connection info
        with connection.cursor() as cursor:
            cursor.execute('SELECT version()')
            version = cursor.fetchone()[0]
            stats['version'] = version

    except Exception as e:
        logger.error(f'Failed to get database stats: {e}')
        stats['error'] = str(e)

    return stats
