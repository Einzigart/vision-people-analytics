"""
Rate limiting middleware for API endpoints.

This middleware provides comprehensive rate limiting functionality including:
- Different limits for authenticated vs unauthenticated users
- Admin user bypass
- Rate limit headers in responses
- 429 Too Many Requests error responses
"""

import time
from django.conf import settings
from django.http import JsonResponse
from django.core.cache import caches
from django.utils import timezone
from django_ratelimit.core import is_ratelimited
from django_ratelimit.exceptions import Ratelimited
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """
    Middleware to enforce rate limits on API endpoints.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.ratelimit_enabled = getattr(settings, 'RATELIMIT_ENABLE', True)
        self.rate_limits = getattr(settings, 'RATE_LIMITS', {})
        self.header_config = getattr(settings, 'RATELIMIT_HEADERS', {})
        
        # Get the cache backend for rate limiting
        self.cache_backend = getattr(settings, 'RATELIMIT_USE_CACHE', 'default')

    def __call__(self, request):
        # Skip rate limiting if disabled
        if not self.ratelimit_enabled:
            response = self.get_response(request)
            return response

        # Skip rate limiting for admin panel and static files
        if self._should_skip_ratelimit(request):
            response = self.get_response(request)
            return response

        # Determine user type and get appropriate rate limit
        user_type = self._get_user_type(request)
        rate_limit = self._get_rate_limit(request, user_type)
        
        if not rate_limit:
            # No rate limit configured for this endpoint/method
            response = self.get_response(request)
            return response

        # Check if request is rate limited
        is_limited = self._check_rate_limit(request, rate_limit)
        
        if is_limited:
            return self._create_rate_limit_response(request, rate_limit)

        # Process the request
        response = self.get_response(request)
        
        # Add rate limit headers to response
        self._add_rate_limit_headers(response, request, rate_limit)
        
        return response

    def _should_skip_ratelimit(self, request):
        """
        Determine if rate limiting should be skipped for this request.
        """
        skip_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/api/health/',  # Health check endpoint
        ]
        
        return any(request.path.startswith(path) for path in skip_paths)

    def _get_user_type(self, request):
        """
        Determine the user type for rate limiting purposes.
        """
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return 'UNAUTHENTICATED'
        
        if request.user.is_staff or request.user.is_superuser:
            return 'ADMIN'
        
        return 'AUTHENTICATED'

    def _get_rate_limit(self, request, user_type):
        """
        Get the appropriate rate limit for this request.
        """
        method = request.method.upper()
        
        # Special handling for detection endpoint
        if request.path.startswith('/api/detections/') and method == 'POST':
            return self.rate_limits.get('DETECTION_ENDPOINT', {}).get('POST')
        
        # Get rate limit for user type and method
        user_limits = self.rate_limits.get(user_type, {})
        return user_limits.get(method)

    def _check_rate_limit(self, request, rate_limit):
        """
        Check if the request should be rate limited.
        """
        try:
            # Create a unique key for this user/IP and endpoint
            key = self._get_rate_limit_key(request)
            cache = caches[self.cache_backend]
            
            # Parse rate limit
            limit_parts = rate_limit.split('/')
            limit = int(limit_parts[0])
            period = limit_parts[1] if len(limit_parts) > 1 else 'm'
            
            # Create cache key
            cache_key = f"rl:{key}:{request.path}:{request.method}:{period}"
            
            # Get current usage
            current_count = cache.get(cache_key, 0)
            
            if current_count >= limit:
                return True
            
            # Increment counter
            period_seconds = self._get_period_seconds(period)
            cache.set(cache_key, current_count + 1, period_seconds)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # On error, allow the request to proceed
            return False

    def _get_rate_limit_key(self, request):
        """
        Generate a unique key for rate limiting.
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user:{request.user.id}"
        else:
            # Use IP address for unauthenticated users
            return self._get_client_ip(request)

    def _get_client_ip(self, request):
        """
        Get the client IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _create_rate_limit_response(self, request, rate_limit):
        """
        Create a 429 Too Many Requests response.
        """
        # Parse rate limit to get reset time
        limit_parts = rate_limit.split('/')
        count = int(limit_parts[0])
        period = limit_parts[1] if len(limit_parts) > 1 else 'm'
        
        # Calculate reset time
        period_seconds = self._get_period_seconds(period)
        reset_time = int(time.time()) + period_seconds
        
        response_data = {
            'error': 'Rate limit exceeded',
            'detail': f'Request was throttled. Expected available in {period_seconds} seconds.',
            'code': 'RATE_LIMIT_EXCEEDED',
            'retry_after': period_seconds
        }
        
        response = JsonResponse(response_data, status=429)
        
        # Add rate limit headers
        if self.header_config.get('ENABLE', True):
            response[self.header_config.get('LIMIT_HEADER', 'X-RateLimit-Limit')] = count
            response[self.header_config.get('REMAINING_HEADER', 'X-RateLimit-Remaining')] = '0'
            response[self.header_config.get('RESET_HEADER', 'X-RateLimit-Reset')] = reset_time
            response['Retry-After'] = str(period_seconds)
        
        return response

    def _add_rate_limit_headers(self, response, request, rate_limit):
        """
        Add rate limit headers to the response.
        """
        if not self.header_config.get('ENABLE', True):
            return

        try:
            # Parse rate limit
            limit_parts = rate_limit.split('/')
            limit = int(limit_parts[0])
            period = limit_parts[1] if len(limit_parts) > 1 else 'm'
            
            # Get current usage
            key = self._get_rate_limit_key(request)
            cache = caches[self.cache_backend]
            
            # Create cache key matching the one used in _check_rate_limit
            cache_key = f"rl:{key}:{request.path}:{request.method}:{period}"
            current_count = cache.get(cache_key, 0)
            
            remaining = max(0, limit - current_count)
            
            # Calculate reset time
            period_seconds = self._get_period_seconds(period)
            reset_time = int(time.time()) + period_seconds
            
            # Add headers
            response[self.header_config.get('LIMIT_HEADER', 'X-RateLimit-Limit')] = limit
            response[self.header_config.get('REMAINING_HEADER', 'X-RateLimit-Remaining')] = remaining
            response[self.header_config.get('RESET_HEADER', 'X-RateLimit-Reset')] = reset_time
            
        except Exception as e:
            logger.warning(f"Error adding rate limit headers: {e}")

    def _get_period_seconds(self, period):
        """
        Convert period string to seconds.
        """
        period_map = {
            's': 1,      # second
            'm': 60,     # minute
            'h': 3600,   # hour
            'd': 86400,  # day
        }
        return period_map.get(period, 60)  # Default to minute


class RateLimitDecoratorMixin:
    """
    Mixin to provide rate limiting decorators for views.
    """
    
    @staticmethod
    def get_rate_limit_decorator(user_type='AUTHENTICATED', method='GET', custom_rate=None):
        """
        Get a rate limit decorator for a specific view.
        
        Args:
            user_type: Type of user ('AUTHENTICATED', 'UNAUTHENTICATED', 'ADMIN')
            method: HTTP method ('GET', 'POST', 'PUT', 'DELETE')
            custom_rate: Custom rate limit (e.g., '100/m') to override defaults
        """
        from django_ratelimit.decorators import ratelimit
        
        if custom_rate:
            rate = custom_rate
        else:
            rate_limits = getattr(settings, 'RATE_LIMITS', {})
            user_limits = rate_limits.get(user_type, {})
            rate = user_limits.get(method, '100/m')  # Default fallback
        
        def key_func(group, request):
            if hasattr(request, 'user') and request.user.is_authenticated:
                return f"user:{request.user.id}"
            else:
                # Use IP for unauthenticated users
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                return ip
        
        return ratelimit(
            key=key_func,
            rate=rate,
            method=method,
            block=True
        )


def rate_limit_exceeded_handler(request, exception):
    """
    Custom handler for rate limit exceeded exceptions.
    """
    response_data = {
        'error': 'Rate limit exceeded',
        'detail': 'Request was throttled. Please try again later.',
        'code': 'RATE_LIMIT_EXCEEDED'
    }
    
    return JsonResponse(response_data, status=429)
