"""
Unit tests for the consolidated API endpoints.
Tests the new /stats/today/ and /stats/range/ endpoints with various parameters.
"""

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from api.models import DailyAggregation, DetectionData
from api.services import AggregationService, DateRangeService, StatsService


class ConsolidatedEndpointsTestCase(TestCase):
    """Test case for consolidated API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create test user
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

        # Clear any existing data to ensure we start with a clean slate
        DetectionData.objects.all().delete()
        DailyAggregation.objects.all().delete()

        # Create test detection data with current day timestamps
        now = timezone.now()
        today = now.replace(hour=12, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)

        # Today's data (set to today's date but with current year/month/day)
        today_real = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        DetectionData.objects.create(
            timestamp=today_real,
            male_0_9=1,
            male_10_19=2,
            male_20_29=3,
            male_30_39=4,
            male_40_49=5,
            male_50_plus=6,
            female_0_9=1,
            female_10_19=2,
            female_20_29=3,
            female_30_39=4,
            female_40_49=5,
            female_50_plus=6,
        )

        # Yesterday's data
        yesterday_real = today_real - timedelta(days=1)
        DetectionData.objects.create(
            timestamp=yesterday_real,
            male_0_9=2,
            male_10_19=3,
            male_20_29=4,
            male_30_39=5,
            male_40_49=6,
            male_50_plus=7,
            female_0_9=2,
            female_10_19=3,
            female_20_29=4,
            female_30_39=5,
            female_40_49=6,
            female_50_plus=7,
        )

        # Update the instance variables to match what we actually created
        self.today = today_real
        self.yesterday = yesterday_real

        # Create daily aggregation for yesterday
        DailyAggregation.objects.create(
            date=yesterday_real.date(),
            male_0_9=2,
            male_10_19=3,
            male_20_29=4,
            male_30_39=5,
            male_40_49=6,
            male_50_plus=7,
            female_0_9=2,
            female_10_19=3,
            female_20_29=4,
            female_30_39=5,
            female_40_49=6,
            female_50_plus=7,
        )

    def test_consolidated_today_stats_basic(self):
        """Test consolidated today stats without demographics"""
        # Format the test date as a string
        test_date_str = self.today.date().isoformat()
        
        url = reverse('consolidated-today-stats')
        response = self.client.get(f"{url}?test_date={test_date_str}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Check response structure
        self.assertIn('date', data)
        self.assertIn('totals', data)
        self.assertIn('hourly_breakdown', data)
        self.assertNotIn(
            'demographics', data
        )  # Should not include demographics by default

        # Check totals
        self.assertEqual(data['totals']['male'], 21)  # 1+2+3+4+5+6
        self.assertEqual(data['totals']['female'], 21)  # 1+2+3+4+5+6
        self.assertEqual(data['totals']['total'], 42)

        # Check date
        self.assertEqual(data['date'], self.today.date().isoformat())

    def test_consolidated_today_stats_with_demographics(self):
        """Test consolidated today stats with demographics"""
        # Format the test date as a string
        test_date_str = self.today.date().isoformat()
        
        url = reverse('consolidated-today-stats')
        response = self.client.get(f"{url}?include_demographics=true&test_date={test_date_str}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Check response structure
        self.assertIn('date', data)
        self.assertIn('totals', data)
        self.assertIn('hourly_breakdown', data)
        self.assertIn('demographics', data)  # Should include demographics

        # Check demographics structure
        self.assertIn('male', data['demographics'])
        self.assertIn('female', data['demographics'])

        # Check specific demographic values
        self.assertEqual(data['demographics']['male']['0-9'], 1)
        self.assertEqual(data['demographics']['male']['50+'], 6)
        self.assertEqual(data['demographics']['female']['0-9'], 1)
        self.assertEqual(data['demographics']['female']['50+'], 6)

    def test_consolidated_range_stats_single_day(self):
        """Test consolidated range stats for a single day"""
        url = reverse(
            'consolidated-range-stats',
            kwargs={
                'start_date': self.today.date().isoformat(),
                'end_date': self.today.date().isoformat(),
            },
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Check response structure for hourly data
        self.assertEqual(data['type'], 'hourly')
        self.assertIn('date', data)
        self.assertIn('totals', data)
        self.assertIn('data', data)  # Hourly breakdown

        # Check totals
        self.assertEqual(data['totals']['male'], 21)
        self.assertEqual(data['totals']['female'], 21)
        self.assertEqual(data['totals']['total'], 42)

    def test_consolidated_range_stats_multiple_days(self):
        """Test consolidated range stats for multiple days"""
        start_date = self.yesterday.date()
        end_date = self.today.date()

        url = reverse(
            'consolidated-range-stats',
            kwargs={
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
            },
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Check response structure for daily data
        self.assertEqual(data['type'], 'daily')
        self.assertIn('start_date', data)
        self.assertIn('end_date', data)
        self.assertIn('data', data)

        # Check that both days are included
        self.assertIn(start_date.isoformat(), data['data'])
        self.assertIn(end_date.isoformat(), data['data'])

        # Check yesterday's data
        yesterday_data = data['data'][start_date.isoformat()]
        self.assertEqual(yesterday_data['male'], 27)  # 2+3+4+5+6+7
        self.assertEqual(yesterday_data['female'], 27)
        self.assertEqual(yesterday_data['total'], 54)

        # Check today's data
        today_data = data['data'][end_date.isoformat()]
        self.assertEqual(today_data['male'], 21)  # 1+2+3+4+5+6
        self.assertEqual(today_data['female'], 21)
        self.assertEqual(today_data['total'], 42)

    def test_consolidated_range_stats_with_demographics(self):
        """Test consolidated range stats with demographics"""
        url = reverse(
            'consolidated-range-stats',
            kwargs={
                'start_date': self.today.date().isoformat(),
                'end_date': self.today.date().isoformat(),
            },
        )
        response = self.client.get(url, {'include_demographics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Should include demographics
        self.assertIn('demographics', data)
        self.assertIn('male', data['demographics'])
        self.assertIn('female', data['demographics'])

    def test_consolidated_range_stats_invalid_date_format(self):
        """Test consolidated range stats with invalid date format"""
        url = reverse(
            'consolidated-range-stats',
            kwargs={'start_date': 'invalid-date', 'end_date': '2023-12-31'},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()

        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['code'], 'INVALID_DATE_FORMAT')

    def test_api_overview_includes_new_endpoints(self):
        """Test that API overview includes the new consolidated endpoints"""
        url = reverse('api-overview')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Check that new consolidated endpoints are included
        self.assertIn('Today Stats (Consolidated)', data)
        self.assertIn('Date Range Stats (Consolidated)', data)

        # Check that legacy endpoints are marked as such
        self.assertIn('Today Stats (Legacy)', data)
        self.assertIn('Time Range (Legacy)', data)


class ServiceClassesTestCase(TestCase):
    """Test case for service classes"""

    def setUp(self):
        """Set up test data"""
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        self.week_ago = self.today - timedelta(days=7)
        self.month_ago = self.today - timedelta(days=31)

        # Create test detection data
        DetectionData.objects.create(
            timestamp=timezone.now(),
            male_0_9=1,
            male_10_19=2,
            male_20_29=3,
            male_30_39=4,
            male_40_49=5,
            male_50_plus=6,
            female_0_9=1,
            female_10_19=2,
            female_20_29=3,
            female_30_39=4,
            female_40_49=5,
            female_50_plus=6,
        )

    def test_date_range_service_single_day(self):
        """Test DateRangeService for single day"""
        result = DateRangeService.get_optimized_queryset(self.today, self.today)

        self.assertEqual(result['data_type'], 'raw')
        self.assertEqual(result['granularity'], 'hourly')
        self.assertEqual(result['days_difference'], 0)

    def test_date_range_service_week(self):
        """Test DateRangeService for a week"""
        result = DateRangeService.get_optimized_queryset(self.week_ago, self.today)

        self.assertEqual(result['data_type'], 'raw')
        self.assertEqual(result['granularity'], 'daily')
        self.assertEqual(result['days_difference'], 7)

    def test_date_range_service_month(self):
        """Test DateRangeService for a month (31 days uses daily aggregation)"""
        result = DateRangeService.get_optimized_queryset(self.month_ago, self.today)

        self.assertEqual(result['data_type'], 'daily_aggregation')
        self.assertEqual(result['granularity'], 'daily')
        self.assertEqual(result['days_difference'], 31)

    def test_date_range_service_long_period(self):
        """Test DateRangeService for a long period (>31 days uses monthly
        aggregation)"""
        long_ago = self.today - timedelta(days=60)
        result = DateRangeService.get_optimized_queryset(long_ago, self.today)

        self.assertEqual(result['data_type'], 'monthly_aggregation')
        self.assertEqual(result['granularity'], 'monthly')
        self.assertEqual(result['days_difference'], 60)

    def test_aggregation_service_compute_totals(self):
        """Test AggregationService compute_totals method"""
        # Clear existing data and create test data
        DetectionData.objects.all().delete()
        
        # Create test data
        test_time = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        DetectionData.objects.create(
            timestamp=test_time,
            male_0_9=1,
            male_10_19=2,
            male_20_29=3,
            male_30_39=4,
            male_40_49=5,
            male_50_plus=6,
            female_0_9=1,
            female_10_19=2,
            female_20_29=3,
            female_30_39=4,
            female_40_49=5,
            female_50_plus=6,
        )
        
        queryset = DetectionData.objects.all()
        totals = AggregationService.compute_totals(queryset)

        self.assertEqual(totals['male'], 21)  # 1+2+3+4+5+6
        self.assertEqual(totals['female'], 21)  # 1+2+3+4+5+6
        self.assertEqual(totals['total'], 42)

    def test_aggregation_service_compute_demographics(self):
        """Test AggregationService compute_demographics method"""
        # Clear existing data and create test data
        DetectionData.objects.all().delete()
        
        # Create test data
        test_time = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        DetectionData.objects.create(
            timestamp=test_time,
            male_0_9=1,
            male_10_19=2,
            male_20_29=3,
            male_30_39=4,
            male_40_49=5,
            male_50_plus=6,
            female_0_9=1,
            female_10_19=2,
            female_20_29=3,
            female_30_39=4,
            female_40_49=5,
            female_50_plus=6,
        )
        
        queryset = DetectionData.objects.all()
        demographics = AggregationService.compute_demographics(queryset)

        self.assertIn('male', demographics)
        self.assertIn('female', demographics)

        # Check specific values
        self.assertEqual(demographics['male']['0-9'], 1)
        self.assertEqual(demographics['male']['50+'], 6)
        self.assertEqual(demographics['female']['0-9'], 1)
        self.assertEqual(demographics['female']['50+'], 6)

    def test_stats_service_format_today_response(self):
        """Test StatsService format_today_response method"""
        totals = {'male': 21, 'female': 21, 'total': 42}
        hours = {'12': {'male': 21, 'female': 21, 'total': 42}}
        demographics = {'male': {'0-9': 1}, 'female': {'0-9': 1}}

        response = StatsService.format_today_response(totals, hours, demographics)

        self.assertIn('date', response)
        self.assertIn('totals', response)
        self.assertIn('hourly_breakdown', response)
        self.assertIn('demographics', response)

        self.assertEqual(response['totals'], totals)
        self.assertEqual(response['hourly_breakdown'], hours)
        self.assertEqual(response['demographics'], demographics)
