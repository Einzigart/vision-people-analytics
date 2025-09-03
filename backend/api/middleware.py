"""Middleware to log request time, DB queries, and cache hits/misses."""

import logging
import time

from django.conf import settings
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Monitor request time, query counts/time, and cache metrics."""

    def process_request(self, request):
        """Start timers and reset counters for this request."""
        request._start_time = time.time()
        request._queries_before = len(connection.queries)

        # Track cache operations for this request
        request._cache_hits = 0
        request._cache_misses = 0

        return None

    def process_response(self, request, response):
        """Log metrics and add debug headers in DEBUG mode."""
        if not hasattr(request, '_start_time'):
            return response

        # Calculate timing
        total_time = time.time() - request._start_time

        # Calculate database queries
        queries_after = len(connection.queries)
        query_count = queries_after - request._queries_before

        # Calculate total query time
        query_time = 0
        if query_count > 0:
            recent_queries = connection.queries[request._queries_before :]
            query_time = sum(float(query['time']) for query in recent_queries)

        # Get cache stats from request if available
        cache_hits = getattr(request, '_cache_hits', 0)
        cache_misses = getattr(request, '_cache_misses', 0)

        # Log performance metrics
        self._log_performance_metrics(
            request=request,
            response=response,
            total_time=total_time,
            query_count=query_count,
            query_time=query_time,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
        )

        # Add performance headers for debugging (only in DEBUG mode)
        if settings.DEBUG:
            response['X-DB-Queries'] = str(query_count)
            response['X-DB-Time'] = f'{query_time:.3f}s'
            response['X-Total-Time'] = f'{total_time:.3f}s'
            response['X-Cache-Hits'] = str(cache_hits)
            response['X-Cache-Misses'] = str(cache_misses)

        return response

    def _log_performance_metrics(
        self,
        request,
        response,
        total_time,
        query_count,
        query_time,
        cache_hits,
        cache_misses,
    ):
        """Write a single structured log entry for the request."""
        # Determine log level based on performance
        if total_time > 2.0:  # Slow requests (>2s)
            log_level = logging.WARNING
            log_prefix = 'SLOW'
        elif total_time > 1.0:  # Medium requests (>1s)
            log_level = logging.INFO
            log_prefix = 'MEDIUM'
        else:  # Fast requests
            log_level = logging.DEBUG
            log_prefix = 'FAST'

        # Calculate cache hit rate
        total_cache_ops = cache_hits + cache_misses
        cache_hit_rate = (
            (cache_hits / total_cache_ops * 100) if total_cache_ops > 0 else 0
        )

        # Log the metrics
        logger.log(
            log_level,
            f'{log_prefix} REQUEST: {request.method} {request.path} | '
            f'Status: {response.status_code} | '
            f'Time: {total_time:.3f}s | '
            f'DB Queries: {query_count} ({query_time:.3f}s) | '
            f'Cache: {cache_hits}H/{cache_misses}M ({cache_hit_rate:.1f}% hit rate)',
        )

        # Log slow queries if any
        if query_time > 0.5 and hasattr(request, '_queries_before'):
            recent_queries = connection.queries[request._queries_before :]
            slow_queries = [q for q in recent_queries if float(q['time']) > 0.1]

            for query in slow_queries:
                logger.warning(
                    f'SLOW QUERY ({query["time"]}s): {query["sql"][:200]}...'
                )


class CacheTrackingMixin:
    """
    Mixin to add cache hit/miss tracking to views.
    """

    def track_cache_hit(self, request):
        """Track a cache hit for this request."""
        if hasattr(request, '_cache_hits'):
            request._cache_hits += 1

    def track_cache_miss(self, request):
        """Track a cache miss for this request."""
        if hasattr(request, '_cache_misses'):
            request._cache_misses += 1


class DatabaseQueryLogger:
    """
    Context manager to log database queries for specific operations.
    """

    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.start_time = None
        self.queries_before = 0

    def __enter__(self):
        self.start_time = time.time()
        self.queries_before = len(connection.queries)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:  # Only log if no exception occurred
            end_time = time.time()
            queries_after = len(connection.queries)
            query_count = queries_after - self.queries_before
            total_time = end_time - self.start_time

            # Calculate query time
            query_time = 0
            if query_count > 0:
                recent_queries = connection.queries[self.queries_before :]
                query_time = sum(float(query['time']) for query in recent_queries)

            logger.debug(
                f"DB OPERATION '{self.operation_name}': "
                f'{query_count} queries in {total_time:.3f}s '
                f'(DB time: {query_time:.3f}s)'
            )


def log_cache_operation(operation, key, hit=None):
    """
    Log cache operations for debugging.

    Args:
        operation: 'get', 'set', 'delete', 'clear'
        key: cache key
        hit: True for hit, False for miss, None for set/delete operations
    """
    if hit is True:
        logger.debug(f"CACHE HIT: {operation} '{key}'")
    elif hit is False:
        logger.debug(f"CACHE MISS: {operation} '{key}'")
    else:
        logger.debug(f"CACHE {operation.upper()}: '{key}'")


def get_performance_stats():
    """
    Get current performance statistics.
    """
    return {
        'database': {
            'total_queries': len(connection.queries),
            'queries_in_last_request': len(connection.queries)
            if connection.queries
            else 0,
        },
        'cache': {
            'backend': settings.CACHES['default']['BACKEND'],
            'status': 'active',
        },
        'note': 'Detailed performance stats available in logs',
    }
