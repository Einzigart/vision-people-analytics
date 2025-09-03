import logging
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.db import connection
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .cache_service import CacheService
from .db_utils import get_database_stats, retry_db_operation
from .middleware import get_performance_stats
from .models import (
    DailyAggregation,
    DetectionData,
    ModelSettings,
    MonthlyAggregation,
)
from .performance_utils import measure_query_performance
from .serializers import (
    DailyAggregationSerializer,  # Will be used for daily age/gender data as well
    DetectionDataInputSerializer,
    DetectionDataSerializer,
    ModelSettingsSerializer,
    MonthlyAggregationSerializer,
)
from .services import AggregationService, DateRangeService, StatsService
from .signals import run_aggregation

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.


@api_view(['GET'])
def api_overview(request):
    """
    API Overview endpoint
    """
    api_urls = {
        'Overview': '/api/',
        'Authentication': '/api/auth/login/',
        'Detection Logs': '/api/detections/',
        'Daily Data': '/api/daily/',  # Aggregated daily data with age/gender
        'Monthly Data': '/api/monthly/',  # Aggregated monthly data with age/gender
        # NEW CONSOLIDATED ENDPOINTS (recommended)
        'Today Stats (Consolidated)': ('/api/stats/today/ '
                                       '(use ?include_demographics=true for '
                                       'age/gender)'),
        'Date Range Stats (Consolidated)': ('/api/stats/range/<start_date>/<end_date>/ '
                                            '(use ?include_demographics=true for '
                                            'age/gender)'),
        # LEGACY ENDPOINTS (deprecated - use consolidated endpoints above)
        'Today Stats (Legacy)': '/api/today/',
        'Today Age Gender Stats (Legacy)': '/api/today-age-gender/',
        'Time Range (Legacy)': '/api/range/<str:start_date>/<str:end_date>/',
        'Age Gender Time Range (Legacy)': ('/api/age-gender-range/'
                                            '<str:start_date>/<str:end_date>/'),
        'Model Settings': '/api/settings/',
        'Public Model Settings': '/api/public-settings/',
    }
    return Response(api_urls)


class LoginView(APIView):
    """
    API endpoint for user authentication
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Please provide both username and password'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED
            )

        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {'token': token.key, 'user_id': user.pk, 'username': user.username}
        )


class DetectionDataAPIView(APIView):
    """
    API endpoint for handling detection data from YOLO model
    """

    def get(self, request):
        last_24h = timezone.now() - timedelta(hours=24)
        detections = DetectionData.objects.filter(timestamp__gte=last_24h).order_by(
            '-timestamp'
        )
        serializer = DetectionDataSerializer(detections, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DetectionDataInputSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            detections_payload = data['detections']
            timestamp = data['timestamp']

            detection_instance = DetectionData(timestamp=timestamp)

            male_details = detections_payload.get('male', {})
            female_details = detections_payload.get('female', {})

            if (
                isinstance(male_details, dict)
                and isinstance(female_details, dict)
                and any(
                    age_key in male_details
                    for age_key in ['0-9', '10-19', '20-29', '30-39', '40-49', '50+']
                )
                and any(
                    age_key in female_details
                    for age_key in ['0-9', '10-19', '20-29', '30-39', '40-49', '50+']
                )
            ):
                detection_instance.male_0_9 = male_details.get('0-9', 0)
                detection_instance.male_10_19 = male_details.get('10-19', 0)
                detection_instance.male_20_29 = male_details.get('20-29', 0)
                detection_instance.male_30_39 = male_details.get('30-39', 0)
                detection_instance.male_40_49 = male_details.get('40-49', 0)
                detection_instance.male_50_plus = male_details.get('50+', 0)

                detection_instance.female_0_9 = female_details.get('0-9', 0)
                detection_instance.female_10_19 = female_details.get('10-19', 0)
                detection_instance.female_20_29 = female_details.get('20-29', 0)
                detection_instance.female_30_39 = female_details.get('30-39', 0)
                detection_instance.female_40_49 = female_details.get('40-49', 0)
                detection_instance.female_50_plus = female_details.get('50+', 0)

                detection_instance.save()

                # Invalidate all stats caches since new data was added
                CacheService.invalidate_all_stats()

                return Response(
                    {
                        'status': 'success',
                        'data': DetectionDataSerializer(detection_instance).data,
                        'message': 'Age-gender data successfully processed into '
                                   'DetectionData',
                    },
                    status=status.HTTP_201_CREATED,
                )

            elif isinstance(male_details, int) and isinstance(female_details, int):
                # Since male_count and female_count are now computed properties,
                # we need to distribute the counts across age groups.
                # For simplicity, we'll put all counts in the 20-29 age group
                detection_instance.male_20_29 = male_details
                detection_instance.female_20_29 = female_details
                detection_instance.save()

                # Invalidate all stats caches since new data was added
                CacheService.invalidate_all_stats()

                return Response(
                    {
                        'status': 'success',
                        'data': DetectionDataSerializer(detection_instance).data,
                        'message': 'Simple detection data successfully processed',
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {
                        'status': 'error',
                        'code': 'INVALID_PAYLOAD_FORMAT',
                        'message': 'Detections payload must contain either detailed '
                                   'age-gender objects or simple male/female '
                                   'integer counts.',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {
                'status': 'error',
                'code': 'VALIDATION_ERROR',
                'message': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class TodayStatsAPIView(APIView):
    """
    API endpoint for today's statistics (basic gender counts)
    """

    def get(self, request):
        today = timezone.localtime(timezone.now())
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)

        today_data = DetectionData.objects.filter(timestamp__gte=today_start)

        # Aggregate male counts from all age groups
        male_total = (
            today_data.aggregate(
                total=Sum('male_0_9')
                + Sum('male_10_19')
                + Sum('male_20_29')
                + Sum('male_30_39')
                + Sum('male_40_49')
                + Sum('male_50_plus')
            )['total']
            or 0
        )

        # Aggregate female counts from all age groups
        female_total = (
            today_data.aggregate(
                total=Sum('female_0_9')
                + Sum('female_10_19')
                + Sum('female_20_29')
                + Sum('female_30_39')
                + Sum('female_40_49')
                + Sum('female_50_plus')
            )['total']
            or 0
        )
        total = male_total + female_total

        hours = {}
        for hour in range(24):
            hour_start = today_start + timedelta(hours=hour)
            hour_end = today_start + timedelta(hours=hour + 1)

            hour_data = today_data.filter(
                timestamp__gte=hour_start, timestamp__lt=hour_end
            )
            hour_male = (
                hour_data.aggregate(
                    total=Sum('male_0_9')
                    + Sum('male_10_19')
                    + Sum('male_20_29')
                    + Sum('male_30_39')
                    + Sum('male_40_49')
                    + Sum('male_50_plus')
                )['total']
                or 0
            )
            hour_female = (
                hour_data.aggregate(
                    total=Sum('female_0_9')
                    + Sum('female_10_19')
                    + Sum('female_20_29')
                    + Sum('female_30_39')
                    + Sum('female_40_49')
                    + Sum('female_50_plus')
                )['total']
                or 0
            )

            hours[str(hour)] = {
                'male': hour_male,
                'female': hour_female,
                'total': hour_male + hour_female,
            }

        male_percentage = (male_total / total * 100) if total > 0 else 0
        female_percentage = (female_total / total * 100) if total > 0 else 0

        result = {
            'date': today_start.date().isoformat(),
            'totals': {'male': male_total, 'female': female_total, 'total': total},
            'percentages': {
                'male': round(male_percentage, 1),
                'female': round(female_percentage, 1),
            },
            'hourly_breakdown': hours,
        }

        return Response(result)


class TodayAgeGenderStatsAPIView(APIView):
    """
    API endpoint for today's age-gender statistics
    """

    def get(self, request):
        today = timezone.localtime(timezone.now())
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)

        today_data = DetectionData.objects.filter(timestamp__gte=today_start)

        age_groups = ['0_9', '10_19', '20_29', '30_39', '40_49', '50_plus']
        age_group_labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50+']

        demographics = {'male': {}, 'female': {}}

        for i, age_group in enumerate(age_groups):
            male_field = f'male_{age_group}'
            female_field = f'female_{age_group}'
            label = age_group_labels[i]

            male_total = (
                today_data.aggregate(Sum(male_field))[f'{male_field}__sum'] or 0
            )
            female_total = (
                today_data.aggregate(Sum(female_field))[f'{female_field}__sum'] or 0
            )

            demographics['male'][label] = male_total
            demographics['female'][label] = female_total

        total_male = sum(demographics['male'].values())
        total_female = sum(demographics['female'].values())
        total = total_male + total_female

        male_percentage = (total_male / total * 100) if total > 0 else 0
        female_percentage = (total_female / total * 100) if total > 0 else 0

        hours = {}
        for hour in range(24):
            hour_start = today_start + timedelta(hours=hour)
            hour_end = today_start + timedelta(hours=hour + 1)
            hour_data = today_data.filter(
                timestamp__gte=hour_start, timestamp__lt=hour_end
            )
            hour_demographics = {'male': {}, 'female': {}}

            for i, age_group in enumerate(age_groups):
                male_field = f'male_{age_group}'
                female_field = f'female_{age_group}'
                label = age_group_labels[i]
                hour_male = (
                    hour_data.aggregate(Sum(male_field))[f'{male_field}__sum'] or 0
                )
                hour_female = (
                    hour_data.aggregate(Sum(female_field))[f'{female_field}__sum'] or 0
                )
                hour_demographics['male'][label] = hour_male
                hour_demographics['female'][label] = hour_female

            hour_total_male = sum(hour_demographics['male'].values())
            hour_total_female = sum(hour_demographics['female'].values())

            hours[str(hour)] = {
                'demographics': hour_demographics,
                'totals': {
                    'male': hour_total_male,
                    'female': hour_total_female,
                    'total': hour_total_male + hour_total_female,
                },
            }

        result = {
            'date': today_start.date().isoformat(),
            'demographics': demographics,
            'totals': {'male': total_male, 'female': total_female, 'total': total},
            'percentages': {
                'male': round(male_percentage, 1),
                'female': round(female_percentage, 1),
            },
            'hourly_breakdown': hours,
        }

        return Response(result)


class ConsolidatedTodayStatsAPIView(APIView):
    """
    Consolidated API endpoint for today's statistics.
    Replaces both /today/ and /today-age-gender/ endpoints.
    Use ?include_demographics=true to get detailed age-gender breakdown.
    """

    @retry_db_operation(max_attempts=3, delay=0.5)
    @measure_query_performance('consolidated_today_stats')
    def get(self, request):
        include_demographics = (
            request.query_params.get('include_demographics', 'false').lower() == 'true'
        )
        no_cache = request.query_params.get('no_cache', 'false').lower() == 'true'
        
        # Allow overriding date for testing
        test_date_str = request.query_params.get('test_date')
        target_date = None
        if test_date_str:
            # Allow test_date in DEBUG mode or when running tests
            if not settings.DEBUG and not hasattr(settings, 'TESTING'):
                test_date_str = None
            else:
                try:
                    target_date = datetime.strptime(test_date_str, '%Y-%m-%d').date()
                except ValueError:
                    target_date = None
                    test_date_str = None

        # Try to get from cache first
        cached_response = CacheService.get_today_stats(include_demographics)
        if cached_response and not test_date_str and not no_cache:
            return Response(cached_response)

        # Cache miss - compute the data
        if target_date:
            # Use the test date for filtering
            today_start = timezone.make_aware(
                datetime.combine(target_date, datetime.min.time())
            )
            today_end = today_start + timedelta(days=1)
            today_data = DetectionData.objects.filter(
                timestamp__gte=today_start, timestamp__lt=today_end
            )
        else:
            # Normal behavior
            today = timezone.localtime(timezone.now())
            target_date = today.date()  # Use today's date for response
            today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
            today_data = DetectionData.objects.filter(timestamp__gte=today_start)

        # Compute totals using service
        totals = AggregationService.compute_totals(today_data)

        # Compute hourly breakdown
        hours = AggregationService.aggregate_by_hour(today_data, target_date)

        # Compute demographics if requested
        demographics = None
        if include_demographics:
            demographics = AggregationService.compute_demographics(today_data)

        # Format response using service
        response = StatsService.format_today_response(totals, hours, demographics, target_date)

        # Cache the response (but not for test dates)
        if not test_date_str and not no_cache:
            CacheService.set_today_stats(response, include_demographics)

        return Response(response)


class DateRangeStatsAPIView(APIView):
    """
    API endpoint for statistics over a custom date range (basic gender counts)
    """

    def get(self, request, start_date, end_date):
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            days_difference = (end - start).days

            if days_difference <= 7:
                start_datetime = timezone.make_aware(
                    datetime.combine(start, datetime.min.time())
                )
                end_datetime = timezone.make_aware(
                    datetime.combine(end + timedelta(days=1), datetime.min.time())
                )
                detections = DetectionData.objects.filter(
                    timestamp__gte=start_datetime, timestamp__lt=end_datetime
                )
                result = self._group_detections_by_day(detections, start, end)
                return Response(result)

            elif (
                days_difference <= 31
            ):  # Use DailyAggregation (now includes age/gender, but this endpoint
                # is for basic counts)
                daily_data = DailyAggregation.objects.filter(
                    date__gte=start, date__lte=end
                ).order_by('date')
                result = self._format_daily_data(
                    daily_data, start, end
                )  # This formats basic counts
                return Response(result)

            else:  # Use MonthlyAggregation (now includes age/gender, but this
                  # endpoint is for basic counts)
                start_month = date(start.year, start.month, 1)
                end_month = date(end.year, end.month, 1)
                months = []
                current_month = start_month
                while current_month <= end_month:
                    months.append(current_month)
                    current_month = current_month + relativedelta(months=1)
                result = self._get_monthly_data(months)  # This formats basic counts
                return Response(result)

        except ValueError:
            return Response(
                {
                    'status': 'error',
                    'code': 'INVALID_DATE_FORMAT',
                    'message': 'Dates should be in YYYY-MM-DD format',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _group_detections_by_day(self, detections, start_date, end_date):
        is_single_day = start_date == end_date
        if is_single_day:
            return self._group_detections_by_hour(detections, start_date)

        days = {}
        current_date = start_date
        while current_date <= end_date:
            day_start = timezone.make_aware(
                datetime.combine(current_date, datetime.min.time())
            )
            day_end = timezone.make_aware(
                datetime.combine(current_date + timedelta(days=1), datetime.min.time())
            )
            day_detections = detections.filter(
                timestamp__gte=day_start, timestamp__lt=day_end
            )
            male_total = (
                day_detections.aggregate(
                    total=Sum('male_0_9')
                    + Sum('male_10_19')
                    + Sum('male_20_29')
                    + Sum('male_30_39')
                    + Sum('male_40_49')
                    + Sum('male_50_plus')
                )['total']
                or 0
            )
            female_total = (
                day_detections.aggregate(
                    total=Sum('female_0_9')
                    + Sum('female_10_19')
                    + Sum('female_20_29')
                    + Sum('female_30_39')
                    + Sum('female_40_49')
                    + Sum('female_50_plus')
                )['total']
                or 0
            )
            days[current_date.isoformat()] = {
                'male': male_total,
                'female': female_total,
                'total': male_total + female_total,
            }
            current_date += timedelta(days=1)
        return {
            'type': 'daily',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'data': days,
        }

    def _group_detections_by_hour(self, detections, target_date):
        hours = {}
        day_start = timezone.make_aware(
            datetime.combine(target_date, datetime.min.time())
        )
        day_detections = detections.filter(
            timestamp__gte=day_start, timestamp__lt=day_start + timedelta(days=1)
        )
        for hour in range(24):
            hour_start = day_start + timedelta(hours=hour)
            hour_detections_in_hour = day_detections.filter(
                timestamp__gte=hour_start, timestamp__lt=hour_start + timedelta(hours=1)
            )
            male_total = (
                hour_detections_in_hour.aggregate(
                    total=Sum('male_0_9')
                    + Sum('male_10_19')
                    + Sum('male_20_29')
                    + Sum('male_30_39')
                    + Sum('male_40_49')
                    + Sum('male_50_plus')
                )['total']
                or 0
            )
            female_total = (
                hour_detections_in_hour.aggregate(
                    total=Sum('female_0_9')
                    + Sum('female_10_19')
                    + Sum('female_20_29')
                    + Sum('female_30_39')
                    + Sum('female_40_49')
                    + Sum('female_50_plus')
                )['total']
                or 0
            )
            hours[str(hour)] = {
                'male': male_total,
                'female': female_total,
                'total': male_total + female_total,
            }
        return {'type': 'hourly', 'date': target_date.isoformat(), 'data': hours}

    def _format_daily_data(self, daily_data, start_date, end_date):
        days = {}
        daily_lookup = {item.date.isoformat(): item for item in daily_data}
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            if date_str in daily_lookup:
                item = daily_lookup[date_str]
                days[date_str] = {
                    'male': item.male_count,
                    'female': item.female_count,
                    'total': item.total_count,
                }
            else:
                days[date_str] = {'male': 0, 'female': 0, 'total': 0}
            current_date += timedelta(days=1)
        return {
            'type': 'daily',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'data': days,
        }

    def _get_monthly_data(self, months):
        monthly_data_map = {}
        for month_date in months:
            try:
                monthly = MonthlyAggregation.objects.get(
                    year=month_date.year, month=month_date.month
                )
                monthly_data_map[month_date.isoformat()[:7]] = {
                    'male': monthly.male_count,
                    'female': monthly.female_count,
                    'total': monthly.total_count,
                }
            except MonthlyAggregation.DoesNotExist:
                monthly_data_map[month_date.isoformat()[:7]] = {
                    'male': 0,
                    'female': 0,
                    'total': 0,
                }
        return {
            'type': 'monthly',
            'start_month': months[0].isoformat()[:7],
            'end_month': months[-1].isoformat()[:7],
            'data': monthly_data_map,
        }


class AgeGenderDateRangeStatsAPIView(APIView):
    """
    API endpoint for age-gender statistics over a custom date range
    """

    def get(self, request, start_date, end_date):
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            days_difference = (end - start).days

            if (
                days_difference <= 31
            ):  # Use DetectionData for up to a month for detailed age/gender
                start_datetime = timezone.make_aware(
                    datetime.combine(start, datetime.min.time())
                )
                end_datetime = timezone.make_aware(
                    datetime.combine(end + timedelta(days=1), datetime.min.time())
                )
                detections = DetectionData.objects.filter(
                    timestamp__gte=start_datetime, timestamp__lt=end_datetime
                )
                if days_difference == 0:
                    result = self._group_age_gender_by_hour(detections, start)
                else:
                    result = self._group_age_gender_by_day(detections, start, end)
            else:  # For longer than a month, use DailyAggregation (which now has
                  # age/gender)
                daily_aggregations = DailyAggregation.objects.filter(
                    date__gte=start, date__lte=end
                ).order_by('date')
                result = self._format_daily_age_gender_data(
                    daily_aggregations, start, end
                )

            return Response(result)

        except ValueError:
            return Response(
                {
                    'status': 'error',
                    'code': 'INVALID_DATE_FORMAT',
                    'message': 'Dates should be in YYYY-MM-DD format',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _format_daily_age_gender_data(self, daily_aggregations, start_date, end_date):
        """Formats DailyAggregation data (which includes age/gender) for the
        response."""
        days = {}
        current_date = start_date
        age_group_labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50+']

        daily_lookup = {item.date.isoformat(): item for item in daily_aggregations}

        while current_date <= end_date:
            date_str = current_date.isoformat()
            demographics = {
                'male': {label: 0 for label in age_group_labels},
                'female': {label: 0 for label in age_group_labels},
            }
            total_male_day = 0
            total_female_day = 0

            if date_str in daily_lookup:
                item = daily_lookup[date_str]
                demographics['male'] = item.male_demographics
                demographics['female'] = item.female_demographics
                total_male_day = item.male_count
                total_female_day = item.female_count

            days[date_str] = {
                'demographics': demographics,
                'totals': {
                    'male': total_male_day,
                    'female': total_female_day,
                    'total': total_male_day + total_female_day,
                },
            }
            current_date += timedelta(days=1)

        return {
            'type': 'daily_age_gender',  # Indicate source is daily aggregations
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'data': days,
        }

    def _group_age_gender_by_day(self, detections, start_date, end_date):
        days = {}
        current_date = start_date
        age_groups = ['0_9', '10_19', '20_29', '30_39', '40_49', '50_plus']
        age_group_labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50+']

        while current_date <= end_date:
            day_start = timezone.make_aware(
                datetime.combine(current_date, datetime.min.time())
            )
            day_end = timezone.make_aware(
                datetime.combine(current_date + timedelta(days=1), datetime.min.time())
            )
            day_detections = detections.filter(
                timestamp__gte=day_start, timestamp__lt=day_end
            )
            demographics = {'male': {}, 'female': {}}

            for i, age_group in enumerate(age_groups):
                male_field, female_field, label = (
                    f'male_{age_group}',
                    f'female_{age_group}',
                    age_group_labels[i],
                )
                male_total = (
                    day_detections.aggregate(Sum(male_field))[f'{male_field}__sum'] or 0
                )
                female_total = (
                    day_detections.aggregate(Sum(female_field))[f'{female_field}__sum']
                    or 0
                )
                demographics['male'][label], demographics['female'][label] = (
                    male_total,
                    female_total,
                )

            total_male, total_female = (
                sum(demographics['male'].values()),
                sum(demographics['female'].values()),
            )
            days[current_date.isoformat()] = {
                'demographics': demographics,
                'totals': {
                    'male': total_male,
                    'female': total_female,
                    'total': total_male + total_female,
                },
            }
            current_date += timedelta(days=1)
        return {
            'type': 'daily_detection_age_gender',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'data': days,
        }

    def _group_age_gender_by_hour(self, detections, target_date):
        hours = {}
        day_start = timezone.make_aware(
            datetime.combine(target_date, datetime.min.time())
        )
        day_detections = detections.filter(
            timestamp__gte=day_start, timestamp__lt=day_start + timedelta(days=1)
        )
        age_groups = ['0_9', '10_19', '20_29', '30_39', '40_49', '50_plus']
        age_group_labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50+']

        for hour in range(24):
            hour_start = day_start + timedelta(hours=hour)
            hour_detections_in_hour = day_detections.filter(
                timestamp__gte=hour_start, timestamp__lt=hour_start + timedelta(hours=1)
            )
            demographics = {'male': {}, 'female': {}}
            for i, age_group in enumerate(age_groups):
                male_field, female_field, label = (
                    f'male_{age_group}',
                    f'female_{age_group}',
                    age_group_labels[i],
                )
                hour_male = (
                    hour_detections_in_hour.aggregate(Sum(male_field))[
                        f'{male_field}__sum'
                    ]
                    or 0
                )
                hour_female = (
                    hour_detections_in_hour.aggregate(Sum(female_field))[
                        f'{female_field}__sum'
                    ]
                    or 0
                )
                demographics['male'][label], demographics['female'][label] = (
                    hour_male,
                    hour_female,
                )
            total_male, total_female = (
                sum(demographics['male'].values()),
                sum(demographics['female'].values()),
            )
            hours[str(hour)] = {
                'demographics': demographics,
                'totals': {
                    'male': total_male,
                    'female': total_female,
                    'total': total_male + total_female,
                },
            }
        return {
            'type': 'hourly_detection_age_gender',
            'date': target_date.isoformat(),
            'data': hours,
        }


class ConsolidatedRangeStatsAPIView(APIView):
    """
    Consolidated API endpoint for date range statistics.
    Replaces both /range/ and /age-gender-range/ endpoints.
    Use ?include_demographics=true to get detailed age-gender breakdown.
    """

    @retry_db_operation(max_attempts=3, delay=0.5)
    @measure_query_performance('consolidated_range_stats')
    def get(self, request, start_date, end_date):
        include_demographics = (
            request.query_params.get('include_demographics', 'false').lower() == 'true'
        )
        no_cache = request.query_params.get('no_cache', 'false').lower() == 'true'

        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()

            # Try to get from cache first
            if not no_cache:
                cached_response = CacheService.get_range_stats(
                    start, end, include_demographics
                )
                if cached_response:
                    return Response(cached_response)

            # Use DateRangeService to get optimized queryset
            optimization_result = DateRangeService.get_optimized_queryset(start, end)
            data_type = optimization_result['data_type']
            granularity = optimization_result['granularity']

            if data_type == 'raw':
                # Use raw DetectionData
                queryset = optimization_result['queryset']

                if granularity == 'hourly':
                    # Single day - hourly breakdown
                    totals = AggregationService.compute_totals(queryset)
                    hours = AggregationService.aggregate_by_hour(queryset, start)
                    demographics = (
                        AggregationService.compute_demographics(queryset)
                        if include_demographics
                        else None
                    )

                    response_data = {
                        'type': 'hourly',
                        'date': start.isoformat(),
                        'totals': totals,
                        'data': hours,
                    }
                    if demographics:
                        response_data['demographics'] = demographics

                    # Cache the response
                    if not no_cache:
                        CacheService.set_range_stats(
                            response_data, start, end, include_demographics
                        )
                    return Response(response_data)

                else:
                    # Multi-day - daily breakdown
                    data = AggregationService.aggregate_by_day(queryset, start, end)
                    demographics = None
                    if include_demographics:
                        demographics = AggregationService.compute_demographics(queryset)

                    response_data = StatsService.format_range_response(
                        data, start, end, 'daily', demographics
                    )
                    # Cache the response
                    if not no_cache:
                        CacheService.set_range_stats(
                            response_data, start, end, include_demographics
                        )
                    return Response(response_data)

            elif data_type == 'daily_aggregation':
                # Use DailyAggregation
                queryset = optimization_result['queryset']

                # Format daily data from aggregations
                days = {}
                daily_lookup = {item.date.isoformat(): item for item in queryset}
                current_date = start

                while current_date <= end:
                    date_str = current_date.isoformat()
                    if date_str in daily_lookup:
                        item = daily_lookup[date_str]
                        days[date_str] = {
                            'male': item.male_count,
                            'female': item.female_count,
                            'total': item.total_count,
                        }

                        if include_demographics:
                            if 'demographics' not in days[date_str]:
                                days[date_str]['demographics'] = {}
                            days[date_str]['demographics'] = {
                                'male': item.male_demographics,
                                'female': item.female_demographics,
                            }
                    else:
                        days[date_str] = {'male': 0, 'female': 0, 'total': 0}
                        if include_demographics:
                            days[date_str]['demographics'] = {'male': {}, 'female': {}}

                    current_date += timedelta(days=1)

                response_data = {
                    'type': 'daily',
                    'start_date': start.isoformat(),
                    'end_date': end.isoformat(),
                    'data': days,
                }

                # Cache the response
                if not no_cache:
                    CacheService.set_range_stats(
                        response_data, start, end, include_demographics
                    )
                return Response(response_data)

            elif data_type == 'monthly_aggregation':
                # Use MonthlyAggregation
                months = optimization_result['months']
                result = StatsService.get_monthly_data(months)

                if include_demographics:
                    # Add demographics to monthly data
                    for month_date in months:
                        month_key = month_date.isoformat()[:7]
                        try:
                            monthly = MonthlyAggregation.objects.get(
                                year=month_date.year, month=month_date.month
                            )
                            result['data'][month_key]['demographics'] = {
                                'male': monthly.male_demographics,
                                'female': monthly.female_demographics,
                            }
                        except MonthlyAggregation.DoesNotExist:
                            result['data'][month_key]['demographics'] = {
                                'male': {},
                                'female': {},
                            }

                # Cache the response
                if not no_cache:
                    CacheService.set_range_stats(result, start, end, include_demographics)
                return Response(result)

        except ValueError:
            return Response(
                {
                    'status': 'error',
                    'code': 'INVALID_DATE_FORMAT',
                    'message': 'Dates should be in YYYY-MM-DD format',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ModelSettingsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Try to get from cache first
        cached_settings = CacheService.get_model_settings()
        if cached_settings:
            return Response(cached_settings)

        # Cache miss - get from database
        settings, created = ModelSettings.objects.get_or_create(id=1)
        serializer = ModelSettingsSerializer(settings)
        response_data = serializer.data

        # Cache the response
        CacheService.set_model_settings(response_data)
        return Response(response_data)

    def put(self, request):
        settings, created = ModelSettings.objects.get_or_create(id=1)
        serializer = ModelSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            settings = serializer.save(updated_by=request.user)
            response_data = ModelSettingsSerializer(settings).data

            # Invalidate cache and set new data
            CacheService.invalidate_model_settings()
            CacheService.set_model_settings(response_data)

            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublicModelSettingsAPIView(APIView):
    """
    Public API endpoint for reading model settings (no authentication required)
    This is specifically for the dummy detection script to fetch settings
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Get current model settings (read-only, public access)"""
        settings, created = ModelSettings.objects.get_or_create(id=1)
        # Return only the essential settings data (no sensitive info)
        return Response(
            {
                'confidence_threshold_person': settings.confidence_threshold_person,
                'confidence_threshold_face': settings.confidence_threshold_face,
                'log_interval_seconds': settings.log_interval_seconds,
                'last_updated': settings.last_updated.isoformat()
                if settings.last_updated
                else None,
            }
        )


class DailyAggregationAPIView(APIView):
    def get(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        limit = request.query_params.get('limit', 30)

        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = 30

        queryset = DailyAggregation.objects.all()

        if start_date_str:
            try:
                queryset = queryset.filter(
                    date__gte=datetime.strptime(start_date_str, '%Y-%m-%d').date()
                )
            except ValueError:
                return Response(
                    {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if end_date_str:
            try:
                queryset = queryset.filter(
                    date__lte=datetime.strptime(end_date_str, '%Y-%m-%d').date()
                )
            except ValueError:
                return Response(
                    {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        daily_data = queryset.order_by('-date')[:limit]
        serializer = DailyAggregationSerializer(
            daily_data, many=True
        )  # Uses the updated serializer
        return Response(serializer.data)


# DailyAgeGenderAggregationAPIView is removed as DailyAggregationAPIView now
# handles this.


class MonthlyAggregationAPIView(APIView):
    def get(self, request):
        logger.debug(
            f'MonthlyAggregationAPIView received params: {request.query_params}'
        )

        start_year = request.query_params.get('start_year')
        start_month = request.query_params.get('start_month')
        end_year = request.query_params.get('end_year')
        end_month = request.query_params.get('end_month')
        limit = request.query_params.get('limit', 12)

        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = 12

        queryset_all = MonthlyAggregation.objects.all()
        logger.debug(
            f'Total MonthlyAggregation records before filtering: {queryset_all.count()}'
        )

        conditions = Q()

        if start_year and start_month:
            try:
                start_y, start_m = int(start_year), int(start_month)
                conditions &= Q(year__gt=start_y) | Q(year=start_y, month__gte=start_m)
            except ValueError:
                logger.error(
                    f'Invalid start_year/start_month: {start_year}/{start_month}'
                )
                return Response(
                    {'error': 'Invalid start_year or start_month format'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if end_year and end_month:
            try:
                end_y, end_m = int(end_year), int(end_month)
                conditions &= Q(year__lt=end_y) | Q(year=end_y, month__lte=end_m)
            except ValueError:
                logger.error(f'Invalid end_year/end_month: {end_year}/{end_month}')
                return Response(
                    {'error': 'Invalid end_year or end_month format'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        logger.debug(f'Constructed filter conditions: {conditions}')

        filtered_queryset = queryset_all
        if conditions != Q():  # Apply filters only if any were constructed
            filtered_queryset = queryset_all.filter(conditions)

        logger.debug(
            f'MonthlyAggregation records after filtering (before limit): '
            f'{filtered_queryset.count()}'
        )

        monthly_data_qs = filtered_queryset.order_by('-year', '-month')[:limit]

        logger.debug(
            f'MonthlyAggregation records after limit: {monthly_data_qs.count()}'
        )

        serializer = MonthlyAggregationSerializer(monthly_data_qs, many=True)
        logger.debug(f'Serialized monthly data: {serializer.data}')
        return Response(serializer.data)


class PerformanceStatsAPIView(APIView):
    """
    API endpoint for performance monitoring statistics.
    Only available to authenticated users.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get basic performance stats
        stats = get_performance_stats()

        # Add cache stats
        stats['cache']['timeouts'] = settings.CACHE_TIMEOUTS

        # Add database connection info
        stats['database']['engine'] = connection.vendor
        stats['database']['name'] = connection.settings_dict['NAME']

        # Add database health check
        db_stats = get_database_stats()
        stats['database'].update(db_stats)

        # Add request info
        stats['request'] = {
            'path': request.path,
            'method': request.method,
            'user': request.user.username,
            'timestamp': timezone.now().isoformat(),
        }

        # Add log file locations
        stats['logs'] = {
            'performance': 'logs/performance.log',
            'api': 'logs/api.log',
        }

        return Response(stats)


class HealthCheckView(APIView):
    """
    Health check endpoint to monitor system status.
    Available without authentication for monitoring purposes.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
        Return system health status including database connectivity.
        """
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': timezone.now().isoformat(),
                'checks': {},
            }

            # Database health check
            try:
                db_stats = get_database_stats()
                health_status['checks']['database'] = {
                    'status': 'healthy'
                    if db_stats.get('connection_healthy')
                    else 'unhealthy',
                    'details': db_stats,
                }
            except Exception as e:
                health_status['checks']['database'] = {
                    'status': 'unhealthy',
                    'error': str(e),
                }
                health_status['status'] = 'degraded'

            # Cache health check
            try:
                from django.core.cache import cache

                cache.set('health_check', 'ok', 30)
                cache_test = cache.get('health_check')
                health_status['checks']['cache'] = {
                    'status': 'healthy' if cache_test == 'ok' else 'unhealthy'
                }
            except Exception as e:
                health_status['checks']['cache'] = {
                    'status': 'unhealthy',
                    'error': str(e),
                }
                health_status['status'] = 'degraded'

            # Determine overall status
            unhealthy_checks = [
                check
                for check in health_status['checks'].values()
                if check['status'] == 'unhealthy'
            ]

            if unhealthy_checks:
                health_status['status'] = 'unhealthy'
                return Response(
                    health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            elif health_status['status'] == 'degraded':
                return Response(health_status, status=status.HTTP_200_OK)
            else:
                return Response(health_status, status=status.HTTP_200_OK)
        except Exception as e:
            # Catch any unexpected error and always return JSON
            return Response(
                {
                    'status': 'unhealthy',
                    'timestamp': timezone.now().isoformat(),
                    'checks': {},
                    'error': str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TriggerAggregationAPIView(APIView):
    """
    API endpoint to manually trigger data aggregation
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        import time

        start_time = time.time()

        try:
            # Get current status
            detection_count = DetectionData.objects.count()
            unaggregated_count = DetectionData.objects.filter(
                is_aggregated=False
            ).count()
            daily_count_before = DailyAggregation.objects.count()
            monthly_count_before = MonthlyAggregation.objects.count()

            if unaggregated_count == 0:
                return Response(
                    {
                        'success': True,
                        'message': 'No unaggregated data found. All data is '
                                   'already aggregated.',
                        'stats': {
                            'detection_records': detection_count,
                            'unaggregated_records': 0,
                            'daily_aggregations': daily_count_before,
                            'monthly_aggregations': monthly_count_before,
                        },
                    }
                )

            # Run aggregation
            run_aggregation()

            # Get results
            daily_count_after = DailyAggregation.objects.count()
            monthly_count_after = MonthlyAggregation.objects.count()
            unaggregated_after = DetectionData.objects.filter(
                is_aggregated=False
            ).count()

            processing_time = round(time.time() - start_time, 2)

            return Response(
                {
                    'success': True,
                    'message': f'Successfully aggregated {unaggregated_count} '
                               f'records in {processing_time} seconds',
                    'stats': {
                        'detection_records': detection_count,
                        'processed_records': unaggregated_count,
                        'remaining_unaggregated': unaggregated_after,
                        'daily_aggregations_created': daily_count_after
                        - daily_count_before,
                        'monthly_aggregations_created': monthly_count_after
                        - monthly_count_before,
                        'total_daily_aggregations': daily_count_after,
                        'total_monthly_aggregations': monthly_count_after,
                        'processing_time_seconds': processing_time,
                    },
                }
            )

        except Exception as e:
            return Response(
                {'success': False, 'message': f'Aggregation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
