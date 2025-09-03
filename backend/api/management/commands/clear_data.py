from django.core.management.base import BaseCommand

from api.models import (
    DailyAggregation,
    DetectionData,
    ModelSettings,
    MonthlyAggregation,
)


class Command(BaseCommand):
    help = 'Clear all detection data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm', action='store_true', help='Confirm deletion without prompting'
        )

    def handle(self, *args, **options):
        confirm = options['confirm']

        # Get counts before deletion
        detection_count = DetectionData.objects.count()
        daily_count = DailyAggregation.objects.count()
        monthly_count = MonthlyAggregation.objects.count()
        settings_count = ModelSettings.objects.count()

        total_count = detection_count + daily_count + monthly_count + settings_count

        if total_count == 0:
            self.stdout.write(self.style.WARNING('No data found to delete.'))
            return

        self.stdout.write('Found data to delete:')
        self.stdout.write(f'- Detection records: {detection_count:,}')
        self.stdout.write(f'- Daily aggregations: {daily_count:,}')
        self.stdout.write(f'- Monthly aggregations: {monthly_count:,}')
        self.stdout.write(f'- Model settings: {settings_count:,}')
        self.stdout.write(f'Total records: {total_count:,}')

        if not confirm:
            response = input(
                '\nAre you sure you want to delete all this data? (yes/no): '
            )
            if response.lower() not in ['yes', 'y']:
                self.stdout.write('Operation cancelled.')
                return

        # Delete all data
        self.stdout.write('Deleting data...')

        DetectionData.objects.all().delete()
        DailyAggregation.objects.all().delete()
        MonthlyAggregation.objects.all().delete()
        ModelSettings.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted all data:\n'
                f'- {detection_count:,} detection records\n'
                f'- {daily_count:,} daily aggregations\n'
                f'- {monthly_count:,} monthly aggregations\n'
                f'- {settings_count:,} model settings'
            )
        )
