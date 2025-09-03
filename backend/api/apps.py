from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        """
        Run setup code when Django starts
        """
        # Register signals

        # Import models and signals here to avoid circular imports
        from .signals import schedule_periodic_aggregation

        # Run the signal handler after migrations
        post_migrate.connect(schedule_periodic_aggregation, sender=self)
