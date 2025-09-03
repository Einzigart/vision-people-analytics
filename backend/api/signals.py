import logging
from datetime import timedelta
from threading import Timer

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from .models import (
    DailyAggregation,
    DetectionData,
    MonthlyAggregation,
)

logger = logging.getLogger(__name__)


def schedule_periodic_aggregation(sender, **kwargs):
    """Kick off aggregation now and schedule a daily run."""
    # Run aggregation immediately on startup
    run_aggregation()

    # Then schedule it to run daily at 3 AM
    schedule_daily_aggregation()


def schedule_daily_aggregation():
    """Schedule daily aggregation at 3 AM local time."""
    now = timezone.localtime(timezone.now())
    target_time = now.replace(hour=3, minute=0, second=0, microsecond=0)

    # If it's already past 3 AM, schedule for tomorrow
    if now.hour >= 3:
        target_time += timedelta(days=1)

    # Calculate seconds until next run
    seconds_until_target = (target_time - now).total_seconds()

    # Schedule the task
    t = Timer(seconds_until_target, run_scheduled_aggregation)
    t.daemon = True  # Allow the thread to exit when the main process exits
    t.start()

    logger.info(
        f'Scheduled data aggregation to run in {seconds_until_target / 3600:.2f} hours'
    )


def run_scheduled_aggregation():
    """Run aggregation and schedule the next run."""
    try:
        # Run aggregation
        run_aggregation()
    except Exception as e:
        logger.error(f'Error in scheduled aggregation: {str(e)}')
    finally:
        # Schedule next run
        schedule_daily_aggregation()


def run_aggregation():
    """Aggregate unprocessed rows into daily and monthly tables."""
    try:
        with transaction.atomic():
            # Get all unaggregated detection data
            raw_data = DetectionData.objects.filter(is_aggregated=False)

            if raw_data.exists():
                record_count = raw_data.count()
                logger.info(f'Starting aggregation of {record_count} records...')

                # Process daily aggregations
                detailed_daily_aggregated_count = aggregate_to_daily_detailed(raw_data)
                logger.info(
                    f'Created {detailed_daily_aggregated_count} daily aggregations'
                )

                # Mark raw data as aggregated in batches for better performance
                batch_size = 1000
                total_updated = 0
                while True:
                    batch = raw_data.filter(is_aggregated=False)[:batch_size]
                    if not batch:
                        break
                    batch_ids = list(batch.values_list('id', flat=True))
                    updated = DetectionData.objects.filter(id__in=batch_ids).update(
                        is_aggregated=True
                    )
                    total_updated += updated
                    if updated < batch_size:
                        break

                # Process monthly aggregations for ALL data (not just older than a year)
                # This will aggregate from the enhanced DailyAggregation to
                # MonthlyAggregation
                monthly_count = aggregate_to_monthly_detailed()
                logger.info(f'Created {monthly_count} monthly aggregations')

                logger.info(
                    f'Aggregated {record_count} raw detection records successfully. '
                    f'Updated {total_updated} records as aggregated.'
                )
            else:
                logger.info('No data to aggregate')
    except Exception as e:
        logger.error(f'Data aggregation error: {str(e)}')
        raise  # Re-raise to let the API endpoint handle it


def aggregate_to_daily(raw_data):
    """Deprecated: use aggregate_to_daily_detailed."""
    # This function is deprecated because male_count, female_count, total_count
    # are now computed properties
    # Use aggregate_to_daily_detailed instead which works with the actual age
    # group fields
    logger.warning(
        'aggregate_to_daily is deprecated - use aggregate_to_daily_detailed instead'
    )
    return 0


# aggregate_to_daily_simple function is removed.


def aggregate_to_daily_detailed(raw_data):
    """Increment daily totals from unaggregated rows (age/gender aware)."""
    from django.db.models.functions import TruncDate

    daily_age_gender_totals = (
        raw_data.annotate(date=TruncDate('timestamp'))
        .values('date')
        .annotate(
            sum_male_0_9=Sum('male_0_9'),
            sum_male_10_19=Sum('male_10_19'),
            sum_male_20_29=Sum('male_20_29'),
            sum_male_30_39=Sum('male_30_39'),
            sum_male_40_49=Sum('male_40_49'),
            sum_male_50_plus=Sum('male_50_plus'),
            sum_female_0_9=Sum('female_0_9'),
            sum_female_10_19=Sum('female_10_19'),
            sum_female_20_29=Sum('female_20_29'),
            sum_female_30_39=Sum('female_30_39'),
            sum_female_40_49=Sum('female_40_49'),
            sum_female_50_plus=Sum('female_50_plus'),
            # Note: male_count, female_count, total_count are computed properties,
            # not database fields
            # They will be calculated automatically by the model's @property methods
        )
    )

    processed_days = 0
    for daily_detail in daily_age_gender_totals:
        # Prepare increments (coalesce None to 0)
        inc = {
            'male_0_9': daily_detail['sum_male_0_9'] or 0,
            'male_10_19': daily_detail['sum_male_10_19'] or 0,
            'male_20_29': daily_detail['sum_male_20_29'] or 0,
            'male_30_39': daily_detail['sum_male_30_39'] or 0,
            'male_40_49': daily_detail['sum_male_40_49'] or 0,
            'male_50_plus': daily_detail['sum_male_50_plus'] or 0,
            'female_0_9': daily_detail['sum_female_0_9'] or 0,
            'female_10_19': daily_detail['sum_female_10_19'] or 0,
            'female_20_29': daily_detail['sum_female_20_29'] or 0,
            'female_30_39': daily_detail['sum_female_30_39'] or 0,
            'female_40_49': daily_detail['sum_female_40_49'] or 0,
            'female_50_plus': daily_detail['sum_female_50_plus'] or 0,
        }

        # Create row if missing, otherwise increment existing values to avoid
        # overwriting previously aggregated data for that date.
        agg, created = DailyAggregation.objects.get_or_create(
            date=daily_detail['date'],
            defaults=inc,
        )

        if not created:
            from django.db.models import F

            DailyAggregation.objects.filter(pk=agg.pk).update(
                male_0_9=F('male_0_9') + inc['male_0_9'],
                male_10_19=F('male_10_19') + inc['male_10_19'],
                male_20_29=F('male_20_29') + inc['male_20_29'],
                male_30_39=F('male_30_39') + inc['male_30_39'],
                male_40_49=F('male_40_49') + inc['male_40_49'],
                male_50_plus=F('male_50_plus') + inc['male_50_plus'],
                female_0_9=F('female_0_9') + inc['female_0_9'],
                female_10_19=F('female_10_19') + inc['female_10_19'],
                female_20_29=F('female_20_29') + inc['female_20_29'],
                female_30_39=F('female_30_39') + inc['female_30_39'],
                female_40_49=F('female_40_49') + inc['female_40_49'],
                female_50_plus=F('female_50_plus') + inc['female_50_plus'],
            )

        processed_days += 1

    return processed_days


def aggregate_to_monthly_detailed():
    """Rebuild monthly totals from daily aggregation (age/gender aware)."""
    # Source model is DailyAggregation
    daily_data = DailyAggregation.objects.all()

    if not daily_data.exists():
        logger.info('No DailyAggregation data to aggregate into monthly summaries.')
        return 0

    from django.db.models.functions import ExtractMonth, ExtractYear

    # Summing fields from DailyAggregation
    monthly_detailed_totals = (
        daily_data.annotate(year=ExtractYear('date'), month=ExtractMonth('date'))
        .values('year', 'month')
        .annotate(
            sum_male_0_9=Sum('male_0_9'),
            sum_male_10_19=Sum('male_10_19'),
            sum_male_20_29=Sum('male_20_29'),
            sum_male_30_39=Sum('male_30_39'),
            sum_male_40_49=Sum('male_40_49'),
            sum_male_50_plus=Sum('male_50_plus'),
            sum_female_0_9=Sum('female_0_9'),
            sum_female_10_19=Sum('female_10_19'),
            sum_female_20_29=Sum('female_20_29'),
            sum_female_30_39=Sum('female_30_39'),
            sum_female_40_49=Sum('female_40_49'),
            sum_female_50_plus=Sum('female_50_plus'),
            # Note: male_count, female_count, total_count are computed properties
            # in DailyAggregation
        )
    )

    aggregated_monthly_count = 0
    for monthly_data in monthly_detailed_totals:
        logger.info(
            f'Processing MonthlyAggregation: Year={monthly_data["year"]}, '
            f'Month={monthly_data["month"]}'
        )

        monthly_agg, created = MonthlyAggregation.objects.update_or_create(
            year=monthly_data['year'],
            month=monthly_data['month'],
            defaults={
                'male_0_9': monthly_data['sum_male_0_9'],
                'male_10_19': monthly_data['sum_male_10_19'],
                'male_20_29': monthly_data['sum_male_20_29'],
                'male_30_39': monthly_data['sum_male_30_39'],
                'male_40_49': monthly_data['sum_male_40_49'],
                'male_50_plus': monthly_data['sum_male_50_plus'],
                'female_0_9': monthly_data['sum_female_0_9'],
                'female_10_19': monthly_data['sum_female_10_19'],
                'female_20_29': monthly_data['sum_female_20_29'],
                'female_30_39': monthly_data['sum_female_30_39'],
                'female_40_49': monthly_data['sum_female_40_49'],
                'female_50_plus': monthly_data['sum_female_50_plus'],
            },
        )
        monthly_agg.save()
        aggregated_monthly_count += 1

    logger.info(
        f'Aggregated {aggregated_monthly_count} months from DailyAggregation '
        f'to MonthlyAggregation.'
    )
    return aggregated_monthly_count


# The old aggregate_to_monthly function is now replaced by
# aggregate_to_monthly_detailed.
# The simple daily aggregation (aggregate_to_daily_simple) is removed.
# The aggregate_to_daily function is kept for now but might be redundant.
