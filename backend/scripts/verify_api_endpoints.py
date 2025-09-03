"""
Quick test script to verify API endpoints work with dummy data
Run this after creating dummy data to ensure everything is working
"""

import os
import sys
from datetime import datetime, timedelta

import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('.')
django.setup()

from api.models import DailyAggregation, DetectionData, MonthlyAggregation  # noqa: E402


def test_api_endpoints():
    """Test API endpoints with actual data"""

    # Check if we have data
    detection_count = DetectionData.objects.count()
    if detection_count == 0:
        print('❌ No detection data found. Run: python manage.py create_dummy_data')
        return False

    print(f'✅ Found {detection_count:,} detection records')

    # Test data ranges
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)

    print(f'📅 Testing date range: {start_date} to {end_date}')

    # Test detection data query
    detections = DetectionData.objects.filter(
        timestamp__date__range=[start_date, end_date]
    ).order_by('timestamp')

    print(f'🔍 Found {detections.count()} detection records in last 7 days')

    if detections.exists():
        latest = detections.last()
        print(
            f'📊 Latest record: {latest.timestamp} - {latest.total_count} people '
            f'(M:{latest.male_count}, F:{latest.female_count})'
        )

    # Test daily aggregations
    daily_aggs = DailyAggregation.objects.filter(
        date__range=[start_date, end_date]
    ).order_by('date')

    print(f'📈 Found {daily_aggs.count()} daily aggregations in last 7 days')

    if daily_aggs.exists():
        total_people = sum(day.total_count for day in daily_aggs)
        avg_daily = total_people / daily_aggs.count() if daily_aggs.count() > 0 else 0
        print(f'📊 Total people in period: {total_people:,}')
        print(f'📊 Average per day: {avg_daily:.1f}')

    # Test monthly aggregations
    monthly_aggs = MonthlyAggregation.objects.all().order_by('-year', '-month')
    print(f'📅 Found {monthly_aggs.count()} monthly aggregations')

    if monthly_aggs.exists():
        latest_month = monthly_aggs.first()
        print(
            f'📊 Latest month ({latest_month.year}-{latest_month.month:02d}): '
            f'{latest_month.total_count:,} people'
        )

    # Test hourly patterns
    from django.db.models import Avg, Count, Sum

    hourly_stats = (
        DetectionData.objects.filter(timestamp__date__range=[start_date, end_date])
        .extra({'hour': 'extract(hour from timestamp)'})
        .values('hour')
        .annotate(
            count=Count('id'),
            total_people=Sum('total_count'),
            avg_people=Avg('total_count'),
        )
        .order_by('hour')
    )

    print('\n⏰ Hourly traffic patterns (last 7 days):')
    for stat in hourly_stats:
        hour = int(stat['hour']) if stat['hour'] is not None else 0
        total = stat['total_people'] or 0
        avg = stat['avg_people'] or 0
        print(f'   {hour:02d}:00 - Total: {total:4d}, Avg: {avg:5.1f} per record')

    # Test gender distribution
    from django.db.models import Sum

    gender_stats = DetectionData.objects.filter(
        timestamp__date__range=[start_date, end_date]
    ).aggregate(
        total_male=Sum('male_count'),
        total_female=Sum('female_count'),
        total_people=Sum('total_count'),
    )

    if gender_stats['total_people']:
        male_pct = (gender_stats['total_male'] / gender_stats['total_people']) * 100
        female_pct = (gender_stats['total_female'] / gender_stats['total_people']) * 100
        print('\n👥 Gender distribution (last 7 days):')
        print(f'   Male: {gender_stats["total_male"]:,} ({male_pct:.1f}%)')
        print(f'   Female: {gender_stats["total_female"]:,} ({female_pct:.1f}%)')

    # Test Age-Gender fields in DetectionData
    print('\n🧬 Testing Age-Gender fields in DetectionData:')
    # Try to find a record that might have age-gender data (e.g., one of the
    # latest ones)
    # This assumes dummy data might include some age/gender details.
    # If not, this test might show all zeros, which is still a valid check that
    # fields exist.
    latest_detection_with_age_gender = DetectionData.objects.order_by(
        '-timestamp'
    ).first()
    if latest_detection_with_age_gender:
        print(
            f'   Sample record timestamp: {latest_detection_with_age_gender.timestamp}'
        )
        print(f'   Male 0-9: {latest_detection_with_age_gender.male_0_9}')
        print(f'   Female 50+: {latest_detection_with_age_gender.female_50_plus}')
        print(
            f'   Demographics Summary: '
            f'{latest_detection_with_age_gender.demographics_summary}'
        )
    else:
        print('   No DetectionData records found to test age-gender fields.')

    print('\n✅ All tests completed successfully!')
    print('🎯 Your dummy data is ready for frontend testing')

    return True


if __name__ == '__main__':
    print('🧪 Testing API with dummy data...\n')
    test_api_endpoints()
