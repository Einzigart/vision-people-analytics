from django.contrib.auth.models import User
from django.db import models


class DetectionData(models.Model):  # This is the new merged model
    """
    Stores raw detection data from YOLO model per minute, including age and
    gender demographics.
    """

    timestamp = models.DateTimeField(db_index=True)

    # Male age groups
    male_0_9 = models.IntegerField(default=0)
    male_10_19 = models.IntegerField(default=0)
    male_20_29 = models.IntegerField(default=0)
    male_30_39 = models.IntegerField(default=0)
    male_40_49 = models.IntegerField(default=0)
    male_50_plus = models.IntegerField(default=0)

    # Female age groups
    female_0_9 = models.IntegerField(default=0)
    female_10_19 = models.IntegerField(default=0)
    female_20_29 = models.IntegerField(default=0)
    female_30_39 = models.IntegerField(default=0)
    female_40_49 = models.IntegerField(default=0)
    female_50_plus = models.IntegerField(default=0)

    is_aggregated = models.BooleanField(default=False)

    @property
    def male_count(self):
        """Computed male count from age groups"""
        return (
            self.male_0_9
            + self.male_10_19
            + self.male_20_29
            + self.male_30_39
            + self.male_40_49
            + self.male_50_plus
        )

    @property
    def female_count(self):
        """Computed female count from age groups"""
        return (
            self.female_0_9
            + self.female_10_19
            + self.female_20_29
            + self.female_30_39
            + self.female_40_49
            + self.female_50_plus
        )

    @property
    def total_count(self):
        """Computed total count from male and female counts"""
        return self.male_count + self.female_count

    @property
    def male_demographics(self):
        """Return male demographics as a dictionary"""
        return {
            '0-9': self.male_0_9,
            '10-19': self.male_10_19,
            '20-29': self.male_20_29,
            '30-39': self.male_30_39,
            '40-49': self.male_40_49,
            '50+': self.male_50_plus,
        }

    @property
    def female_demographics(self):
        """Return female demographics as a dictionary"""
        return {
            '0-9': self.female_0_9,
            '10-19': self.female_10_19,
            '20-29': self.female_20_29,
            '30-39': self.female_30_39,
            '40-49': self.female_40_49,
            '50+': self.female_50_plus,
        }

    @property
    def demographics_summary(self):
        """Return full demographics summary"""
        return {'male': self.male_demographics, 'female': self.female_demographics}

    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['is_aggregated']),
        ]
        verbose_name_plural = 'Detection Logs'

    def __str__(self):
        return (f'Detection Log at {self.timestamp}: {self.total_count} people '
                f'({self.male_count} M, {self.female_count} F)')


# AgeGenderDetection class has been removed. All its functionality is merged
# into DetectionData.


class DailyAggregation(models.Model):
    """
    Stores daily aggregated data for historical analysis, including age and
    gender demographics.
    """

    date = models.DateField(unique=True, db_index=True)

    # Male age groups (from DailyAgeGenderAggregation)
    male_0_9 = models.IntegerField(default=0)
    male_10_19 = models.IntegerField(default=0)
    male_20_29 = models.IntegerField(default=0)
    male_30_39 = models.IntegerField(default=0)
    male_40_49 = models.IntegerField(default=0)
    male_50_plus = models.IntegerField(default=0)

    # Female age groups (from DailyAgeGenderAggregation)
    female_0_9 = models.IntegerField(default=0)
    female_10_19 = models.IntegerField(default=0)
    female_20_29 = models.IntegerField(default=0)
    female_30_39 = models.IntegerField(default=0)
    female_40_49 = models.IntegerField(default=0)
    female_50_plus = models.IntegerField(default=0)

    @property
    def male_count(self):
        """Computed male count from age groups"""
        return (
            self.male_0_9
            + self.male_10_19
            + self.male_20_29
            + self.male_30_39
            + self.male_40_49
            + self.male_50_plus
        )

    @property
    def female_count(self):
        """Computed female count from age groups"""
        return (
            self.female_0_9
            + self.female_10_19
            + self.female_20_29
            + self.female_30_39
            + self.female_40_49
            + self.female_50_plus
        )

    @property
    def total_count(self):
        """Computed total count from male and female counts"""
        return self.male_count + self.female_count

    @property
    def male_demographics(self):
        """Return male demographics as a dictionary"""
        return {
            '0-9': self.male_0_9,
            '10-19': self.male_10_19,
            '20-29': self.male_20_29,
            '30-39': self.male_30_39,
            '40-49': self.male_40_49,
            '50+': self.male_50_plus,
        }

    @property
    def female_demographics(self):
        """Return female demographics as a dictionary"""
        return {
            '0-9': self.female_0_9,
            '10-19': self.female_10_19,
            '20-29': self.female_20_29,
            '30-39': self.female_30_39,
            '40-49': self.female_40_49,
            '50+': self.female_50_plus,
        }

    @property
    def demographics_summary(self):
        """Return full demographics summary"""
        return {'male': self.male_demographics, 'female': self.female_demographics}

    class Meta:
        ordering = ['-date']
        verbose_name_plural = (
            'Daily Aggregations (incl. Age/Gender)'  # Updated verbose name
        )

    def __str__(self):
        return (f'Daily Summary for {self.date}: {self.total_count} people '
                f'(M:{self.male_count}, F:{self.female_count})')


# DailyAgeGenderAggregation class has been removed. Its fields and functionality
# are merged into DailyAggregation.


class MonthlyAggregation(models.Model):
    """
    Stores monthly aggregated data, including age and gender demographics, for
    long-term historical analysis.
    This is now the main monthly aggregation model (MonthlyAggregation will be
    merged into this).
    """

    year = models.IntegerField()
    month = models.IntegerField()

    # Male age groups
    male_0_9 = models.IntegerField(default=0)
    male_10_19 = models.IntegerField(default=0)
    male_20_29 = models.IntegerField(default=0)
    male_30_39 = models.IntegerField(default=0)
    male_40_49 = models.IntegerField(default=0)
    male_50_plus = models.IntegerField(default=0)

    # Female age groups
    female_0_9 = models.IntegerField(default=0)
    female_10_19 = models.IntegerField(default=0)
    female_20_29 = models.IntegerField(default=0)
    female_30_39 = models.IntegerField(default=0)
    female_40_49 = models.IntegerField(default=0)
    female_50_plus = models.IntegerField(default=0)

    @property
    def male_count(self):
        """Computed male count from age groups"""
        return (
            self.male_0_9
            + self.male_10_19
            + self.male_20_29
            + self.male_30_39
            + self.male_40_49
            + self.male_50_plus
        )

    @property
    def female_count(self):
        """Computed female count from age groups"""
        return (
            self.female_0_9
            + self.female_10_19
            + self.female_20_29
            + self.female_30_39
            + self.female_40_49
            + self.female_50_plus
        )

    @property
    def total_count(self):
        """Computed total count from male and female counts"""
        return self.male_count + self.female_count

    @property
    def total_male(self):
        """Legacy property - same as male_count"""
        return self.male_count

    @property
    def total_female(self):
        """Legacy property - same as female_count"""
        return self.female_count

    @property
    def male_demographics(self):
        """Return male demographics as a dictionary"""
        return {
            '0-9': self.male_0_9,
            '10-19': self.male_10_19,
            '20-29': self.male_20_29,
            '30-39': self.male_30_39,
            '40-49': self.male_40_49,
            '50+': self.male_50_plus,
        }

    @property
    def female_demographics(self):
        """Return female demographics as a dictionary"""
        return {
            '0-9': self.female_0_9,
            '10-19': self.female_10_19,
            '20-29': self.female_20_29,
            '30-39': self.female_30_39,
            '40-49': self.female_40_49,
            '50+': self.female_50_plus,
        }

    @property
    def demographics_summary(self):
        """Return full demographics summary"""
        return {'male': self.male_demographics, 'female': self.female_demographics}

    class Meta:
        db_table = 'api_monthlyaggregation'
        unique_together = ('year', 'month')
        ordering = ['-year', '-month']
        verbose_name_plural = ('Monthly Age Gender Aggregations '
                               '(incl. Basic Counts)')

    def __str__(self):
        return (f'Monthly Summary for {self.year}-{self.month:02d}: '
                f'{self.total_count} people (M:{self.male_count}, '
                f'F:{self.female_count})')


# MonthlyAggregation class will be removed. All its functionality is merged
# into MonthlyAggregation.


class ModelSettings(models.Model):
    """
    Stores configuration settings for the detection model
    """

    # Person detection confidence threshold
    confidence_threshold_person = models.FloatField(
        default=0.5, help_text='Confidence threshold for person detection (0.0-1.0)'
    )

    # Face detection confidence threshold
    confidence_threshold_face = models.FloatField(
        default=0.5, help_text='Confidence threshold for face detection (0.0-1.0)'
    )

    # Log interval in seconds
    log_interval_seconds = models.IntegerField(
        default=60, help_text='Interval in seconds for logging detection data'
    )

    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = 'Model Settings'

    def save(self, *args, **kwargs):
        # Ensure only one settings record exists
        if not self.pk and ModelSettings.objects.exists():
            # Update existing record instead of creating new one
            existing = ModelSettings.objects.first()
            existing.confidence_threshold_person = self.confidence_threshold_person
            existing.confidence_threshold_face = self.confidence_threshold_face
            existing.log_interval_seconds = self.log_interval_seconds
            existing.updated_by = self.updated_by
            existing.save()
            return existing
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get the current settings or create default ones"""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'confidence_threshold_person': 0.5,
                'confidence_threshold_face': 0.5,
                'log_interval_seconds': 60,
            },
        )
        return settings

    def __str__(self):
        return f'Detection Model Settings (Last updated: {self.last_updated})'
