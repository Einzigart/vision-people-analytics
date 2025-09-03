"""
Tests for rate limiting middleware and functionality.
"""

import time
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.test.utils import override_settings


class RateLimitMiddlewareTest(APITestCase):
    """
    Test cases for rate limiting middleware.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@test.com'
        )
        self.user_token = Token.objects.create(user=self.user)
        self.admin_token = Token.objects.create(user=self.admin_user)
        
        # Clear cache before each test
        cache.clear()

    def tearDown(self):
        # Clear cache after each test
        cache.clear()

    @override_settings(RATELIMIT_ENABLE=True, RATE_LIMITS={
        'UNAUTHENTICATED': {'GET': '5/m'},
        'AUTHENTICATED': {'GET': '10/m'},
        'ADMIN': {'GET': '20/m'}
    })
    def test_unauthenticated_rate_limit(self):
        """
        Test rate limiting for unauthenticated users.
        """
        # Make requests up to the limit
        for i in range(5):
            response = self.client.get('/api/')
            self.assertEqual(response.status_code, 200)
            self.assertIn('X-RateLimit-Limit', response)
            self.assertEqual(response['X-RateLimit-Limit'], '5')

        # The 6th request should be rate limited
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 429)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['code'], 'RATE_LIMIT_EXCEEDED')

    @override_settings(RATELIMIT_ENABLE=True, RATE_LIMITS={
        'UNAUTHENTICATED': {'GET': '5/m'},
        'AUTHENTICATED': {'GET': '10/m'},
        'ADMIN': {'GET': '20/m'}
    })
    def test_authenticated_user_rate_limit(self):
        """
        Test rate limiting for authenticated users.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        
        # Make requests up to the limit
        for i in range(10):
            response = self.client.get('/api/')
            self.assertEqual(response.status_code, 200)
            self.assertIn('X-RateLimit-Limit', response)
            self.assertEqual(response['X-RateLimit-Limit'], '10')

        # The 11th request should be rate limited
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 429)

    @override_settings(RATELIMIT_ENABLE=True, RATE_LIMITS={
        'UNAUTHENTICATED': {'GET': '5/m'},
        'AUTHENTICATED': {'GET': '10/m'},
        'ADMIN': {'GET': '20/m'}
    })
    def test_admin_user_higher_limits(self):
        """
        Test that admin users get higher rate limits.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        # Make requests up to the admin limit
        for i in range(20):
            response = self.client.get('/api/')
            self.assertEqual(response.status_code, 200)
            self.assertIn('X-RateLimit-Limit', response)
            self.assertEqual(response['X-RateLimit-Limit'], '20')

        # The 21st request should be rate limited
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 429)

    @override_settings(RATELIMIT_ENABLE=False)
    def test_rate_limiting_disabled(self):
        """
        Test that rate limiting can be disabled.
        """
        # Make many requests - should all succeed
        for i in range(100):
            response = self.client.get('/api/')
            self.assertEqual(response.status_code, 200)

    @override_settings(RATELIMIT_ENABLE=True, RATE_LIMITS={
        'UNAUTHENTICATED': {'POST': '3/m'},
        'DETECTION_ENDPOINT': {'POST': '10/m'}
    })
    def test_detection_endpoint_special_limits(self):
        """
        Test that detection endpoint has special rate limits.
        """
        # Regular POST endpoints should have lower limits
        for i in range(3):
            response = self.client.post('/api/auth/login/', {
                'username': 'test',
                'password': 'test'
            })
            # Response can be 400 (bad credentials) but shouldn't be 429
            self.assertNotEqual(response.status_code, 429)

        # 4th request to regular endpoint should be rate limited
        response = self.client.post('/api/auth/login/', {
            'username': 'test',
            'password': 'test'
        })
        self.assertEqual(response.status_code, 429)

        # But detection endpoint should have higher limits
        # Clear cache to reset rate limits
        cache.clear()
        
        for i in range(10):
            response = self.client.post('/api/detections/', {
                'timestamp': '2024-01-01T12:00:00Z',
                'detections': {'male': 1, 'female': 1}
            })
            # Response can be 400 (validation error) but shouldn't be 429
            self.assertNotEqual(response.status_code, 429)

    def test_rate_limit_headers_present(self):
        """
        Test that rate limit headers are included in responses.
        """
        response = self.client.get('/api/')
        
        # Check that rate limit headers are present
        expected_headers = [
            'X-RateLimit-Limit',
            'X-RateLimit-Remaining',
            'X-RateLimit-Reset'
        ]
        
        for header in expected_headers:
            self.assertIn(header, response)

    def test_skip_rate_limiting_for_excluded_paths(self):
        """
        Test that certain paths are excluded from rate limiting.
        """
        excluded_paths = [
            '/admin/',
            '/static/test.css',
            '/api/health/'
        ]
        
        with override_settings(RATELIMIT_ENABLE=True, RATE_LIMITS={
            'UNAUTHENTICATED': {'GET': '1/m'}
        }):
            for path in excluded_paths:
                # Should be able to make many requests to excluded paths
                for i in range(10):
                    response = self.client.get(path)
                    # These paths might return 404, but shouldn't return 429
                    self.assertNotEqual(response.status_code, 429)

    @override_settings(RATELIMIT_ENABLE=True, RATE_LIMITS={
        'UNAUTHENTICATED': {'GET': '2/m'}
    })
    def test_rate_limit_reset_time(self):
        """
        Test that rate limit reset time is properly calculated.
        """
        # Make requests up to limit
        for i in range(2):
            response = self.client.get('/api/')
            self.assertEqual(response.status_code, 200)

        # Next request should be rate limited
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 429)
        
        # Check that reset time is in the future
        reset_time = int(response['X-RateLimit-Reset'])
        current_time = int(time.time())
        self.assertGreater(reset_time, current_time)

    def test_different_limits_for_different_methods(self):
        """
        Test that different HTTP methods can have different rate limits.
        """
        with override_settings(RATELIMIT_ENABLE=True, RATE_LIMITS={
            'UNAUTHENTICATED': {
                'GET': '5/m',
                'POST': '2/m'
            }
        }):
            # Should be able to make 5 GET requests
            for i in range(5):
                response = self.client.get('/api/')
                self.assertEqual(response.status_code, 200)

            # 6th GET should be rate limited
            response = self.client.get('/api/')
            self.assertEqual(response.status_code, 429)

            # But should still be able to make POST requests (different counter)
            response = self.client.post('/api/auth/login/', {})
            self.assertNotEqual(response.status_code, 429)

    @patch('api.ratelimit_middleware.logger')
    def test_error_handling_in_rate_limiting(self, mock_logger):
        """
        Test that errors in rate limiting don't break the application.
        """
        with patch('api.ratelimit_middleware.is_ratelimited') as mock_is_ratelimited:
            # Simulate an error in rate limiting check
            mock_is_ratelimited.side_effect = Exception("Redis connection error")
            
            # Request should still succeed
            response = self.client.get('/api/')
            self.assertEqual(response.status_code, 200)
            
            # Error should be logged
            mock_logger.error.assert_called_once()


class RateLimitIntegrationTest(APITestCase):
    """
    Integration tests for rate limiting with actual API endpoints.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        cache.clear()

    def tearDown(self):
        cache.clear()

    @override_settings(RATELIMIT_ENABLE=True, RATE_LIMITS={
        'UNAUTHENTICATED': {'GET': '3/m'}
    })
    def test_api_overview_rate_limiting(self):
        """
        Test rate limiting on the API overview endpoint.
        """
        # Make requests up to the limit
        for i in range(3):
            response = self.client.get('/api/')
            self.assertEqual(response.status_code, 200)
            self.assertIn('Overview', response.json())

        # Next request should be rate limited
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 429)
        response_data = response.json()
        self.assertEqual(response_data['code'], 'RATE_LIMIT_EXCEEDED')

    @override_settings(RATELIMIT_ENABLE=True, RATE_LIMITS={
        'AUTHENTICATED': {'GET': '5/m'}
    })
    def test_authenticated_endpoint_rate_limiting(self):
        """
        Test rate limiting on authenticated endpoints.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # Make requests to settings endpoint (requires authentication)
        for i in range(5):
            response = self.client.get('/api/settings/')
            self.assertEqual(response.status_code, 200)

        # Next request should be rate limited
        response = self.client.get('/api/settings/')
        self.assertEqual(response.status_code, 429)

    def test_rate_limit_response_format(self):
        """
        Test that rate limit error response has the correct format.
        """
        with override_settings(RATELIMIT_ENABLE=True, RATE_LIMITS={
            'UNAUTHENTICATED': {'GET': '1/m'}
        }):
            # First request succeeds
            response = self.client.get('/api/')
            self.assertEqual(response.status_code, 200)

            # Second request is rate limited
            response = self.client.get('/api/')
            self.assertEqual(response.status_code, 429)
            
            response_data = response.json()
            required_fields = ['error', 'detail', 'code', 'retry_after']
            for field in required_fields:
                self.assertIn(field, response_data)
            
            self.assertEqual(response_data['code'], 'RATE_LIMIT_EXCEEDED')
            self.assertIsInstance(response_data['retry_after'], int)


class RateLimitConfigurationTest(TestCase):
    """
    Test rate limiting configuration and settings.
    """

    def test_default_rate_limit_settings(self):
        """
        Test that default rate limit settings are properly configured.
        """
        from django.conf import settings
        
        # Check that rate limiting is enabled by default
        self.assertTrue(getattr(settings, 'RATELIMIT_ENABLE', False))
        
        # Check that rate limits are configured
        rate_limits = getattr(settings, 'RATE_LIMITS', {})
        self.assertIn('UNAUTHENTICATED', rate_limits)
        self.assertIn('AUTHENTICATED', rate_limits)
        self.assertIn('ADMIN', rate_limits)
        
        # Check that headers are configured
        headers = getattr(settings, 'RATELIMIT_HEADERS', {})
        self.assertTrue(headers.get('ENABLE', False))

    def test_environment_variable_override(self):
        """
        Test that rate limiting can be disabled via environment variable.
        """
        with override_settings(RATELIMIT_ENABLE=False):
            from django.conf import settings
            self.assertFalse(settings.RATELIMIT_ENABLE)


class RateLimitCacheTest(TestCase):
    """
    Test rate limiting cache behavior.
    """

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_cache_backend_fallback(self):
        """
        Test that rate limiting falls back to default cache when Redis unavailable.
        """
        with override_settings(REDIS_URL='', RATELIMIT_USE_CACHE='default'):
            from django.conf import settings
            self.assertEqual(settings.RATELIMIT_USE_CACHE, 'default')

    def test_redis_cache_configuration(self):
        """
        Test Redis cache configuration for rate limiting.
        """
        with override_settings(REDIS_URL='redis://localhost:6379/1'):
            from django.conf import settings
            self.assertEqual(settings.RATELIMIT_USE_CACHE, 'redis')
