#!/usr/bin/env python
"""
Quick test to verify aggregation is working
"""

import os
import sys

import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import DailyAggregation, DetectionData, MonthlyAggregation  # noqa: E402


def quick_status_check():
    """Quick check of current data status"""
    print('Quick Status Check')  # Removed emoji for Windows compatibility
    print('=' * 40)

    detection_count = DetectionData.objects.count()
    unaggregated_count = DetectionData.objects.filter(is_aggregated=False).count()
    daily_count = DailyAggregation.objects.count()
    monthly_count = MonthlyAggregation.objects.count()

    print(f'Detection records: {detection_count:,}')
    print(f'Unaggregated: {unaggregated_count:,}')
    print(f'Daily aggregations: {daily_count:,}')
    print(f'Monthly aggregations: {monthly_count:,}')

    if daily_count > 0:
        print('\nSUCCESS: Daily aggregations exist!')
        recent_daily = DailyAggregation.objects.order_by('-date').first()
        print(f'   Latest: {recent_daily.date} - {recent_daily.total_count} people')
    else:
        print('\nNo daily aggregations found')

    if monthly_count > 0:
        print('SUCCESS: Monthly aggregations exist!')
        recent_monthly = MonthlyAggregation.objects.order_by('-year', '-month').first()
        print(
            f'   Latest: {recent_monthly.year}-{recent_monthly.month:02d} - '
            f'{recent_monthly.total_count} people'
        )
    else:
        print('No monthly aggregations found')

    if unaggregated_count == 0:
        print('\nAll data is aggregated!')
    else:
        print(f'\n{unaggregated_count:,} records still need aggregation')


if __name__ == '__main__':
    quick_status_check()
