"""Cache service for API responses with simple invalidation."""

import hashlib
import logging
from datetime import date, datetime

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

# Import performance tracking
try:
    from .middleware import log_cache_operation
except ImportError:
    # Fallback if middleware is not available
    def log_cache_operation(operation, key, hit=None):
        pass


class CacheService:
    """Centralized cache operations and key management."""

    # Cache key prefixes for different data types
    PREFIXES = {
        'TODAY_STATS': 'today_stats',
        'RANGE_STATS': 'range_stats',
        'DAILY_AGG': 'daily_agg',
        'MONTHLY_AGG': 'monthly_agg',
        'MODEL_SETTINGS': 'model_settings',
        'DETECTION_LOGS': 'detection_logs',
    }

    @staticmethod
    def _generate_cache_key(prefix: str, *args, **kwargs) -> str:
        """
        Generate a consistent cache key from prefix and parameters.
        """
        # Create a string from all arguments
        key_parts = [prefix]

        # Add positional arguments
        for arg in args:
            if isinstance(arg, (date, datetime)):
                key_parts.append(arg.isoformat())
            else:
                key_parts.append(str(arg))

        # Add keyword arguments (sorted for consistency)
        for key, value in sorted(kwargs.items()):
            if isinstance(value, (date, datetime)):
                key_parts.append(f'{key}:{value.isoformat()}')
            else:
                key_parts.append(f'{key}:{value}')

        # Join and hash for consistent length
        key_string = '|'.join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()

        return f'ta_project:{prefix}:{key_hash}'

    @staticmethod
    def _get_timeout(cache_type: str) -> int:
        """
        Get cache timeout for a specific cache type.
        """
        return getattr(settings, 'CACHE_TIMEOUTS', {}).get(cache_type, 300)

    @classmethod
    def get_today_stats(cls, include_demographics: bool = False) -> dict:
        """
        Get cached today's stats or return None if not cached.
        """
        cache_key = cls._generate_cache_key(
            cls.PREFIXES['TODAY_STATS'],
            timezone.localdate(),
            include_demographics=include_demographics,
        )

        result = cache.get(cache_key)
        log_cache_operation('get', cache_key, hit=(result is not None))
        if result:
            logger.debug(
                f'Cache HIT for today stats (demographics={include_demographics})'
            )
        else:
            logger.debug(
                f'Cache MISS for today stats (demographics={include_demographics})'
            )

        return result

    @classmethod
    def set_today_stats(cls, data: dict, include_demographics: bool = False) -> None:
        """
        Cache today's stats data.
        """
        cache_key = cls._generate_cache_key(
            cls.PREFIXES['TODAY_STATS'],
            timezone.localdate(),
            include_demographics=include_demographics,
        )

        timeout = cls._get_timeout('TODAY_STATS')
        cache.set(cache_key, data, timeout)
        log_cache_operation('set', cache_key)
        logger.debug(
            f'Cached today stats (demographics={include_demographics}) for {timeout}s'
        )

    @classmethod
    def get_range_stats(
        cls, start_date: date, end_date: date, include_demographics: bool = False
    ) -> dict:
        """
        Get cached range stats or return None if not cached.
        """
        cache_key = cls._generate_cache_key(
            cls.PREFIXES['RANGE_STATS'],
            start_date,
            end_date,
            include_demographics=include_demographics,
        )

        result = cache.get(cache_key)
        if result:
            logger.debug(
                f'Cache HIT for range stats {start_date} to {end_date} '
                f'(demographics={include_demographics})'
            )
        else:
            logger.debug(
                f'Cache MISS for range stats {start_date} to {end_date} '
                f'(demographics={include_demographics})'
            )

        return result

    @classmethod
    def set_range_stats(
        cls,
        data: dict,
        start_date: date,
        end_date: date,
        include_demographics: bool = False,
    ) -> None:
        """
        Cache range stats data.
        """
        cache_key = cls._generate_cache_key(
            cls.PREFIXES['RANGE_STATS'],
            start_date,
            end_date,
            include_demographics=include_demographics,
        )

        # Base timeout from settings
        timeout = cls._get_timeout('RANGE_STATS')

        # Dynamic TTL: if the requested range includes "today" (live data),
        # reduce the TTL to be closer to TODAY_STATS to reflect updates faster.
        try:
            end_date_only = (
                end_date.date() if isinstance(end_date, datetime) else end_date
            )
            if isinstance(end_date_only, date) and end_date_only >= timezone.localdate():
                live_timeout = cls._get_timeout('TODAY_STATS')  # e.g., 60s
                timeout = min(timeout, live_timeout)
        except Exception:
            # If anything goes wrong determining dates, keep the base timeout
            pass

        cache.set(cache_key, data, timeout)
        logger.debug(
            f'Cached range stats {start_date} to {end_date} '
            f'(demographics={include_demographics}) for {timeout}s'
        )

    @classmethod
    def get_daily_aggregation(
        cls, start_date: date = None, end_date: date = None, limit: int = 30
    ) -> list:
        """
        Get cached daily aggregation data.
        """
        cache_key = cls._generate_cache_key(
            cls.PREFIXES['DAILY_AGG'],
            start_date or 'none',
            end_date or 'none',
            limit=limit,
        )

        result = cache.get(cache_key)
        if result:
            logger.debug(f'Cache HIT for daily aggregation (limit={limit})')
        else:
            logger.debug(f'Cache MISS for daily aggregation (limit={limit})')

        return result

    @classmethod
    def set_daily_aggregation(
        cls, data: list, start_date: date = None, end_date: date = None, limit: int = 30
    ) -> None:
        """
        Cache daily aggregation data.
        """
        cache_key = cls._generate_cache_key(
            cls.PREFIXES['DAILY_AGG'],
            start_date or 'none',
            end_date or 'none',
            limit=limit,
        )

        timeout = cls._get_timeout('DAILY_AGGREGATION')
        cache.set(cache_key, data, timeout)
        logger.debug(f'Cached daily aggregation (limit={limit}) for {timeout}s')

    @classmethod
    def get_monthly_aggregation(
        cls,
        start_year: int = None,
        start_month: int = None,
        end_year: int = None,
        end_month: int = None,
        limit: int = 12,
    ) -> list:
        """
        Get cached monthly aggregation data.
        """
        cache_key = cls._generate_cache_key(
            cls.PREFIXES['MONTHLY_AGG'],
            start_year or 'none',
            start_month or 'none',
            end_year or 'none',
            end_month or 'none',
            limit=limit,
        )

        result = cache.get(cache_key)
        if result:
            logger.debug(f'Cache HIT for monthly aggregation (limit={limit})')
        else:
            logger.debug(f'Cache MISS for monthly aggregation (limit={limit})')

        return result

    @classmethod
    def set_monthly_aggregation(
        cls,
        data: list,
        start_year: int = None,
        start_month: int = None,
        end_year: int = None,
        end_month: int = None,
        limit: int = 12,
    ) -> None:
        """
        Cache monthly aggregation data.
        """
        cache_key = cls._generate_cache_key(
            cls.PREFIXES['MONTHLY_AGG'],
            start_year or 'none',
            start_month or 'none',
            end_year or 'none',
            end_month or 'none',
            limit=limit,
        )

        timeout = cls._get_timeout('MONTHLY_AGGREGATION')
        cache.set(cache_key, data, timeout)
        logger.debug(f'Cached monthly aggregation (limit={limit}) for {timeout}s')

    @classmethod
    def get_model_settings(cls) -> dict:
        """
        Get cached model settings.
        """
        cache_key = cls._generate_cache_key(cls.PREFIXES['MODEL_SETTINGS'])

        result = cache.get(cache_key)
        if result:
            logger.debug('Cache HIT for model settings')
        else:
            logger.debug('Cache MISS for model settings')

        return result

    @classmethod
    def set_model_settings(cls, data: dict) -> None:
        """
        Cache model settings data.
        """
        cache_key = cls._generate_cache_key(cls.PREFIXES['MODEL_SETTINGS'])

        timeout = cls._get_timeout('MODEL_SETTINGS')
        cache.set(cache_key, data, timeout)
        logger.debug(f'Cached model settings for {timeout}s')

    @classmethod
    def invalidate_all_stats(cls) -> None:
        """
        Invalidate all stats caches when new detection data is added.
        This should be called when new DetectionData is created.
        """
        # Get all cache keys that start with our prefixes
        # Note: This is a simple implementation. For Redis, we'd use pattern matching
        cache.clear()  # For simplicity, clear all cache
        logger.info('Invalidated all stats caches due to new detection data')

    @classmethod
    def invalidate_model_settings(cls) -> None:
        """
        Invalidate model settings cache when settings are updated.
        """
        cache_key = cls._generate_cache_key(cls.PREFIXES['MODEL_SETTINGS'])
        cache.delete(cache_key)
        logger.info('Invalidated model settings cache')

    @classmethod
    def get_cache_stats(cls) -> dict:
        """
        Get cache statistics for monitoring.
        """
        # This is a basic implementation - more detailed stats would require Redis
        return {
            'backend': 'django.core.cache.backends.locmem.LocMemCache',
            'status': 'active',
            'note': 'Detailed cache statistics require Redis backend',
        }
