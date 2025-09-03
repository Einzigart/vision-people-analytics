"""
Performance monitoring utilities for the TA Project API.
Provides tools to measure and optimize database query performance.
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Dict

from django.conf import settings
from django.db import connection

logger = logging.getLogger(__name__)


def measure_query_performance(operation_name: str = None):
    """
    Decorator to measure database query performance for API endpoints.

    Args:
        operation_name: Optional name for the operation being measured
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get initial query count
            queries_before = len(connection.queries)
            start_time = time.time()

            try:
                result = func(*args, **kwargs)

                # Calculate performance metrics
                end_time = time.time()
                queries_after = len(connection.queries)
                query_count = queries_after - queries_before
                total_time = end_time - start_time

                # Calculate total query time
                query_time = 0
                if query_count > 0:
                    recent_queries = connection.queries[queries_before:]
                    query_time = sum(float(query['time']) for query in recent_queries)

                # Log performance metrics
                op_name = operation_name or func.__name__
                logger.info(
                    f'PERFORMANCE [{op_name}]: '
                    f'{query_count} queries in {total_time:.3f}s '
                    f'(DB time: {query_time:.3f}s, '
                    f'Python time: {total_time - query_time:.3f}s)'
                )

                # Log slow operations
                if total_time > 1.0:
                    logger.warning(
                        f'SLOW OPERATION [{op_name}]: {total_time:.3f}s total, '
                        f'{query_count} queries, {query_time:.3f}s DB time'
                    )

                # Log inefficient query patterns
                if query_count > 10:
                    logger.warning(
                        f'HIGH QUERY COUNT [{op_name}]: {query_count} queries - '
                        f'consider optimization'
                    )

                return result

            except Exception as e:
                end_time = time.time()
                total_time = end_time - start_time
                op_name = operation_name or func.__name__
                logger.error(f'ERROR [{op_name}]: {str(e)} after {total_time:.3f}s')
                raise

        return wrapper

    return decorator


def analyze_query_patterns(queries: list) -> Dict[str, Any]:
    """
    Analyze database query patterns to identify optimization opportunities.

    Args:
        queries: List of Django query dictionaries

    Returns:
        Dictionary with analysis results
    """
    if not queries:
        return {'total_queries': 0, 'total_time': 0, 'patterns': []}

    total_time = sum(float(q['time']) for q in queries)
    slow_queries = [q for q in queries if float(q['time']) > 0.1]

    # Identify common query patterns
    patterns = {}
    for query in queries:
        sql = query['sql'].strip()
        # Extract table name from query
        if 'FROM' in sql.upper():
            table_part = sql.upper().split('FROM')[1].split()[0]
            table_name = table_part.strip('"').replace('`', '')
            patterns[table_name] = patterns.get(table_name, 0) + 1

    return {
        'total_queries': len(queries),
        'total_time': total_time,
        'slow_queries': len(slow_queries),
        'slowest_query_time': max(float(q['time']) for q in queries) if queries else 0,
        'table_access_patterns': patterns,
        'optimization_suggestions': _get_optimization_suggestions(queries, patterns),
    }


def _get_optimization_suggestions(queries: list, patterns: Dict[str, int]) -> list:
    """
    Generate optimization suggestions based on query analysis.
    """
    suggestions = []

    # Check for N+1 query patterns
    if len(queries) > 10:
        suggestions.append(
            'High query count detected - consider using select_related() or '
            'prefetch_related() to reduce N+1 queries'
        )

    # Check for repeated table access
    for table, count in patterns.items():
        if count > 5:
            suggestions.append(
                f"Table '{table}' accessed {count} times - consider aggregating "
                f'queries or using bulk operations'
            )

    # Check for slow queries
    slow_queries = [q for q in queries if float(q['time']) > 0.1]
    if slow_queries:
        suggestions.append(
            f'{len(slow_queries)} slow queries detected - consider adding '
            f'database indexes or optimizing query structure'
        )

    return suggestions


class QueryProfiler:
    """
    Context manager for profiling database queries in a code block.
    """

    def __init__(self, operation_name: str = 'Unknown'):
        self.operation_name = operation_name
        self.start_time = None
        self.queries_before = 0

    def __enter__(self):
        self.start_time = time.time()
        self.queries_before = len(connection.queries)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        queries_after = len(connection.queries)

        total_time = end_time - self.start_time
        query_count = queries_after - self.queries_before

        if query_count > 0:
            recent_queries = connection.queries[self.queries_before :]
            query_time = sum(float(query['time']) for query in recent_queries)

            # Analyze query patterns
            analysis = analyze_query_patterns(recent_queries)

            logger.info(
                f'QUERY PROFILE [{self.operation_name}]: '
                f'{query_count} queries in {total_time:.3f}s '
                f'(DB: {query_time:.3f}s, Python: {total_time - query_time:.3f}s)'
            )

            # Log optimization suggestions
            if analysis['optimization_suggestions']:
                for suggestion in analysis['optimization_suggestions']:
                    logger.info(
                        f'OPTIMIZATION TIP [{self.operation_name}]: {suggestion}'
                    )


def get_performance_summary() -> Dict[str, Any]:
    """
    Get a summary of current performance metrics.
    """
    return {
        'database': {
            'vendor': connection.vendor,
            'total_queries_this_request': len(connection.queries),
        },
        'cache': {
            'backend': settings.CACHES['default']['BACKEND'],
            'timeouts': getattr(settings, 'CACHE_TIMEOUTS', {}),
        },
        'optimization_tips': [
            'Use consolidated API endpoints for better performance',
            'Enable caching for frequently accessed data',
            'Use database indexes for time-series queries',
            'Consider pagination for large datasets',
        ],
    }
