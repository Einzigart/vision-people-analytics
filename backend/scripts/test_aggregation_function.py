#!/usr/bin/env python
"""
Test script to debug aggregation issues
Run this to test aggregation directly
"""

import os
import sys

import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import DailyAggregation, DetectionData, MonthlyAggregation  # noqa: E402
from api.signals import run_aggregation  # noqa: E402


def test_aggregation():
    """Test the aggregation function directly."""
    print('🔍 Testing Aggregation Function')
    print('=' * 50)

    # Check current data status
    detection_count = DetectionData.objects.count()
    unaggregated_count = DetectionData.objects.filter(is_aggregated=False).count()
    daily_count_before = DailyAggregation.objects.count()
    monthly_count_before = MonthlyAggregation.objects.count()

    print('📊 Current Status:')
    print(f'   • Detection records: {detection_count:,}')
    print(f'   • Unaggregated records: {unaggregated_count:,}')
    print(f'   • Daily aggregations: {daily_count_before:,}')
    print(f'   • Monthly aggregations: {monthly_count_before:,}')

    if unaggregated_count == 0:
        print('⚠️ No unaggregated data found!')
        print('   Marking some data as unaggregated for testing...')
        # Mark last 100 records as unaggregated for testing
        DetectionData.objects.order_by('-timestamp')[:100].update(is_aggregated=False)
        unaggregated_count = DetectionData.objects.filter(is_aggregated=False).count()
        print(f'   • Now have {unaggregated_count:,} unaggregated records')

    print('\n🔄 Running aggregation...')

    try:
        # Run aggregation
        run_aggregation()
        print('✅ Aggregation function completed without errors')

        # Check results
        daily_count_after = DailyAggregation.objects.count()
        monthly_count_after = MonthlyAggregation.objects.count()
        unaggregated_after = DetectionData.objects.filter(is_aggregated=False).count()

        print('\n📈 Results:')
        print(
            f'   • Daily aggregations: {daily_count_before:,} → {daily_count_after:,} '
            f'(+{daily_count_after - daily_count_before:,})'
        )
        print(
            f'   • Monthly aggregations: {monthly_count_before:,} → '
            f'{monthly_count_after:,} '
            f'(+{monthly_count_after - monthly_count_before:,})'
        )
        print(f'   • Remaining unaggregated: {unaggregated_after:,}')

        if daily_count_after > daily_count_before:
            print('🎉 SUCCESS: Daily aggregations were created!')
        else:
            print('❌ ISSUE: No daily aggregations were created')

        if monthly_count_after > monthly_count_before:
            print('🎉 SUCCESS: Monthly aggregations were created!')
        else:
            print('❌ ISSUE: No monthly aggregations were created')

        # Show sample data
        print('\n📋 Sample Daily Aggregations:')
        recent_daily = DailyAggregation.objects.order_by('-date')[:3]
        for daily in recent_daily:
            print(
                f'   • {daily.date}: {daily.male_count}M + {daily.female_count}F = '
                f'{daily.total_count} total'
            )

        print('\n📋 Sample Monthly Aggregations:')
        recent_monthly = MonthlyAggregation.objects.order_by('-year', '-month')[:3]
        for monthly in recent_monthly:
            print(
                f'   • {monthly.year}-{monthly.month:02d}: {monthly.male_count}M + '
                f'{monthly.female_count}F = {monthly.total_count} total'
            )

    except Exception as e:
        print(f'❌ ERROR: Aggregation failed with error: {str(e)}')
        import traceback

        print('\n🔍 Full traceback:')
        traceback.print_exc()


def check_data_sample():
    """Check a sample of detection data to see if it looks correct."""
    print('\n🔍 Checking Sample Detection Data')
    print('=' * 50)

    sample = DetectionData.objects.order_by('-timestamp')[:5]

    for i, record in enumerate(sample, 1):
        total_people = (
            record.male_0_9
            + record.male_10_19
            + record.male_20_29
            + record.male_30_39
            + record.male_40_49
            + record.male_50_plus
            + record.female_0_9
            + record.female_10_19
            + record.female_20_29
            + record.female_30_39
            + record.female_40_49
            + record.female_50_plus
        )

        print(
            f'   {i}. {record.timestamp}: {total_people} people, aggregated: '
            f'{record.is_aggregated}'
        )


if __name__ == '__main__':
    check_data_sample()
    test_aggregation()
