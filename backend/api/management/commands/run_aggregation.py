from django.core.management.base import BaseCommand

from api.models import DailyAggregation, DetectionData, MonthlyAggregation
from api.signals import run_aggregation


class Command(BaseCommand):
    help = ('Manually trigger data aggregation from DetectionData to '
            'DailyAggregation and MonthlyAggregation')

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force aggregation even if data is already marked as aggregated',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output during aggregation',
        )

    def handle(self, *args, **options):
        force = options['force']
        verbose = options['verbose']

        self.stdout.write(self.style.HTTP_INFO('🔄 Starting data aggregation...'))

        # Show current data status
        detection_count = DetectionData.objects.count()
        unaggregated_count = DetectionData.objects.filter(is_aggregated=False).count()
        daily_count = DailyAggregation.objects.count()
        monthly_count = MonthlyAggregation.objects.count()

        self.stdout.write('📊 Current data status:')
        self.stdout.write(f'   • Detection records: {detection_count:,}')
        self.stdout.write(f'   • Unaggregated records: {unaggregated_count:,}')
        self.stdout.write(f'   • Daily aggregations: {daily_count:,}')
        self.stdout.write(f'   • Monthly aggregations: {monthly_count:,}')

        if unaggregated_count == 0 and not force:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️ No unaggregated data found. Use --force to '
                    're-aggregate all data.'
                )
            )
            return

        if force:
            self.stdout.write(
                self.style.WARNING('🔄 Force mode: Marking all data as unaggregated...')
            )
            DetectionData.objects.update(is_aggregated=False)
            unaggregated_count = detection_count

        # Run aggregation
        try:
            if verbose:
                self.stdout.write(
                    f'🔄 Processing {unaggregated_count:,} unaggregated records...'
                )

            run_aggregation()

            # Show results
            new_daily_count = DailyAggregation.objects.count()
            new_monthly_count = MonthlyAggregation.objects.count()
            new_unaggregated_count = DetectionData.objects.filter(
                is_aggregated=False
            ).count()

            self.stdout.write(
                self.style.SUCCESS('✅ Aggregation completed successfully!')
            )
            self.stdout.write('📈 Results:')
            self.stdout.write(
                f'   • Daily aggregations: {daily_count:,} → {new_daily_count:,} '
                f'(+{new_daily_count - daily_count:,})'
            )
            self.stdout.write(
                f'   • Monthly aggregations: {monthly_count:,} → {new_monthly_count:,} '
                f'(+{new_monthly_count - monthly_count:,})'
            )
            self.stdout.write(
                f'   • Remaining unaggregated: {new_unaggregated_count:,}'
            )

            if new_unaggregated_count == 0:
                self.stdout.write(
                    self.style.SUCCESS('🎉 All data has been successfully aggregated!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️ {new_unaggregated_count:,} records remain unaggregated'
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Aggregation failed: {str(e)}'))
            if verbose:
                import traceback

                self.stdout.write(traceback.format_exc())
