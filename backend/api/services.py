"""
Service classes for API logic consolidation.
These services centralize common logic to reduce view complexity.
"""

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from django.db.models import QuerySet, Sum
from django.utils import timezone

from .models import DailyAggregation, DetectionData, MonthlyAggregation


class DateRangeService:
    """Service for handling date range logic and optimization"""

    @staticmethod
    def get_optimized_queryset(start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Centralized logic for choosing raw vs aggregated data based on date range.
        Returns a dictionary with queryset and metadata about the optimization choice.
        """
        days_difference = (end_date - start_date).days

        if days_difference == 0:
            # Single day - use raw DetectionData for hourly breakdown
            start_datetime = timezone.make_aware(
                datetime.combine(start_date, datetime.min.time())
            )
            end_datetime = timezone.make_aware(
                datetime.combine(start_date + timedelta(days=1), datetime.min.time())
            )
            queryset = DetectionData.objects.filter(
                timestamp__gte=start_datetime, timestamp__lt=end_datetime
            )
            return {
                'queryset': queryset,
                'data_type': 'raw',
                'granularity': 'hourly',
                'days_difference': days_difference,
            }

        elif days_difference <= 7:
            # Up to a week - use raw DetectionData for daily breakdown
            start_datetime = timezone.make_aware(
                datetime.combine(start_date, datetime.min.time())
            )
            end_datetime = timezone.make_aware(
                datetime.combine(end_date + timedelta(days=1), datetime.min.time())
            )
            queryset = DetectionData.objects.filter(
                timestamp__gte=start_datetime, timestamp__lt=end_datetime
            )
            return {
                'queryset': queryset,
                'data_type': 'raw',
                'granularity': 'daily',
                'days_difference': days_difference,
            }

        elif days_difference <= 31:
            # Up to a month - use DailyAggregation
            queryset = DailyAggregation.objects.filter(
                date__gte=start_date, date__lte=end_date
            ).order_by('date')
            return {
                'queryset': queryset,
                'data_type': 'daily_aggregation',
                'granularity': 'daily',
                'days_difference': days_difference,
            }

        else:
            # More than a month - use MonthlyAggregation
            start_month = date(start_date.year, start_date.month, 1)
            end_month = date(end_date.year, end_date.month, 1)
            months = []
            current_month = start_month
            while current_month <= end_month:
                months.append(current_month)
                current_month = current_month + relativedelta(months=1)

            return {
                'queryset': None,  # Will be handled differently for monthly data
                'data_type': 'monthly_aggregation',
                'granularity': 'monthly',
                'days_difference': days_difference,
                'months': months,
            }


class AggregationService:
    """Service for computing demographics and aggregations"""

    @staticmethod
    def compute_demographics(queryset: QuerySet) -> Dict[str, Dict[str, int]]:
        """
        Centralized demographics calculation from a queryset.
        Works with both DetectionData and aggregation models.
        """
        age_groups = ['0_9', '10_19', '20_29', '30_39', '40_49', '50_plus']
        age_group_labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50+']

        demographics = {'male': {}, 'female': {}}

        for i, age_group in enumerate(age_groups):
            male_field = f'male_{age_group}'
            female_field = f'female_{age_group}'
            label = age_group_labels[i]

            male_sum = queryset.aggregate(Sum(male_field))[f'{male_field}__sum'] or 0
            female_sum = (
                queryset.aggregate(Sum(female_field))[f'{female_field}__sum'] or 0
            )

            demographics['male'][label] = male_sum
            demographics['female'][label] = female_sum

        return demographics

    @staticmethod
    def compute_totals(queryset: QuerySet) -> Dict[str, int]:
        """
        Compute total counts from age group fields.
        """
        age_groups = ['0_9', '10_19', '20_29', '30_39', '40_49', '50_plus']

        male_total = 0
        female_total = 0

        for age_group in age_groups:
            male_field = f'male_{age_group}'
            female_field = f'female_{age_group}'

            male_sum = queryset.aggregate(Sum(male_field))[f'{male_field}__sum'] or 0
            female_sum = (
                queryset.aggregate(Sum(female_field))[f'{female_field}__sum'] or 0
            )

            male_total += male_sum
            female_total += female_sum

        return {
            'male': male_total,
            'female': female_total,
            'total': male_total + female_total,
        }

    @staticmethod
    def aggregate_by_hour(
        queryset: QuerySet, target_date: date
    ) -> Dict[str, Dict[str, int]]:
        """
        Aggregate data by hour for a specific date using optimized single query.
        """
        from django.db.models import Sum
        from django.db.models.functions import Extract

        day_start = timezone.make_aware(
            datetime.combine(target_date, datetime.min.time())
        )
        day_end = day_start + timedelta(days=1)

        # Use a single query with GROUP BY hour to get all hours at once
        hourly_aggregates = (
            queryset.filter(timestamp__gte=day_start, timestamp__lt=day_end)
            .annotate(hour=Extract('timestamp', 'hour'))
            .values('hour')
            .annotate(
                male_total=Sum('male_0_9')
                + Sum('male_10_19')
                + Sum('male_20_29')
                + Sum('male_30_39')
                + Sum('male_40_49')
                + Sum('male_50_plus'),
                female_total=Sum('female_0_9')
                + Sum('female_10_19')
                + Sum('female_20_29')
                + Sum('female_30_39')
                + Sum('female_40_49')
                + Sum('female_50_plus'),
            )
            .order_by('hour')
        )

        # Create lookup dictionary from query results
        hourly_lookup = {
            item['hour']: {
                'male': item['male_total'] or 0,
                'female': item['female_total'] or 0,
                'total': (item['male_total'] or 0) + (item['female_total'] or 0),
            }
            for item in hourly_aggregates
        }

        # Fill in missing hours with zero values
        hours = {}
        for hour in range(24):
            hours[str(hour)] = hourly_lookup.get(
                hour, {'male': 0, 'female': 0, 'total': 0}
            )

        return hours

    @staticmethod
    def aggregate_by_day(
        queryset: QuerySet, start_date: date, end_date: date
    ) -> Dict[str, Dict[str, int]]:
        """
        Aggregate data by day for a date range using optimized single query.
        """
        from django.db.models import Sum
        from django.db.models.functions import TruncDate

        # Use a single query with GROUP BY date to get all days at once
        daily_aggregates = (
            queryset.annotate(date=TruncDate('timestamp'))
            .values('date')
            .annotate(
                male_total=Sum('male_0_9')
                + Sum('male_10_19')
                + Sum('male_20_29')
                + Sum('male_30_39')
                + Sum('male_40_49')
                + Sum('male_50_plus'),
                female_total=Sum('female_0_9')
                + Sum('female_10_19')
                + Sum('female_20_29')
                + Sum('female_30_39')
                + Sum('female_40_49')
                + Sum('female_50_plus'),
            )
            .order_by('date')
        )

        # Create lookup dictionary from query results
        daily_lookup = {
            item['date'].isoformat(): {
                'male': item['male_total'] or 0,
                'female': item['female_total'] or 0,
                'total': (item['male_total'] or 0) + (item['female_total'] or 0),
            }
            for item in daily_aggregates
        }

        # Fill in missing days with zero values
        days = {}
        current_date = start_date
        while current_date <= end_date:
            date_key = current_date.isoformat()
            days[date_key] = daily_lookup.get(
                date_key, {'male': 0, 'female': 0, 'total': 0}
            )
            current_date += timedelta(days=1)

        return days


class StatsService:
    """Service for formatting statistics responses"""

    @staticmethod
    def format_stats_response(
        data: Dict[str, Any], include_demographics: bool = False
    ) -> Dict[str, Any]:
        """
        Unified response formatting for statistics endpoints.
        """
        response = {'type': data.get('type', 'unknown'), 'data': data.get('data', {})}

        # Add date range information if available
        if 'start_date' in data:
            response['start_date'] = data['start_date']
        if 'end_date' in data:
            response['end_date'] = data['end_date']
        if 'date' in data:
            response['date'] = data['date']

        # Add demographics if requested and available
        if include_demographics and 'demographics' in data:
            response['demographics'] = data['demographics']

        # Add totals if available
        if 'totals' in data:
            response['totals'] = data['totals']

        return response

    @staticmethod
    def format_today_response(
        totals: Dict[str, int],
        hours: Dict[str, Dict[str, int]],
        demographics: Optional[Dict[str, Dict[str, int]]] = None,
        target_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Format today's statistics response.
        """
        # Use the target_date if provided, otherwise use today's date
        response_date = target_date or timezone.localtime(timezone.now()).date()
        
        response = {
            'date': response_date.isoformat(),
            'totals': totals,
            'hourly_breakdown': hours,
        }

        if demographics:
            response['demographics'] = demographics

        return response

    @staticmethod
    def format_range_response(
        data: Dict[str, Dict[str, int]],
        start_date: date,
        end_date: date,
        granularity: str,
        demographics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Format date range statistics response.
        """
        response = {
            'type': granularity,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'data': data,
        }

        if demographics:
            response['demographics'] = demographics

        return response

    @staticmethod
    def get_monthly_data(months: List[date]) -> Dict[str, Any]:
        """
        Get monthly aggregation data for specified months.
        """
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
