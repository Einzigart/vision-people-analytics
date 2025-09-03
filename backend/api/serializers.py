from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    DailyAggregation,  # Now includes age/gender fields
    DetectionData,
    ModelSettings,
    MonthlyAggregation,  # Now includes age/gender fields
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class DetectionDataSerializer(serializers.ModelSerializer):
    demographics = serializers.SerializerMethodField()

    class Meta:
        model = DetectionData
        fields = [
            'id',
            'timestamp',
            'male_count',
            'female_count',
            'total_count',
            'male_0_9',
            'male_10_19',
            'male_20_29',
            'male_30_39',
            'male_40_49',
            'male_50_plus',
            'female_0_9',
            'female_10_19',
            'female_20_29',
            'female_30_39',
            'female_40_49',
            'female_50_plus',
            'demographics',
        ]

    def get_demographics(self, obj):
        return obj.demographics_summary


class DailyAggregationSerializer(serializers.ModelSerializer):
    demographics = serializers.SerializerMethodField()

    class Meta:
        model = DailyAggregation
        # All fields from the merged DailyAggregation model
        fields = [
            'id',
            'date',
            'male_count',
            'female_count',
            'total_count',  # Overall counts
            'male_0_9',
            'male_10_19',
            'male_20_29',
            'male_30_39',
            'male_40_49',
            'male_50_plus',  # Male age groups
            'female_0_9',
            'female_10_19',
            'female_20_29',
            'female_30_39',
            'female_40_49',
            'female_50_plus',  # Female age groups
            'demographics',  # Combined demographics summary
        ]

    def get_demographics(self, obj):
        # Use aggregated demographics properties
        return obj.demographics_summary


# DailyAgeGenderAggregationSerializer is removed.


class MonthlyAggregationSerializer(serializers.ModelSerializer):
    month_name = serializers.SerializerMethodField()
    demographics = serializers.SerializerMethodField()

    class Meta:
        model = MonthlyAggregation
        # All fields from the merged MonthlyAggregation model
        fields = [
            'id',
            'year',
            'month',
            'month_name',
            'male_count',
            'female_count',
            'total_count',  # Overall counts
            'male_0_9',
            'male_10_19',
            'male_20_29',
            'male_30_39',
            'male_40_49',
            'male_50_plus',  # Male age groups
            'female_0_9',
            'female_10_19',
            'female_20_29',
            'female_30_39',
            'female_40_49',
            'female_50_plus',  # Female age groups
            'demographics',  # Combined demographics summary
        ]

    def get_month_name(self, obj):
        month_names = [
            'January',
            'February',
            'March',
            'April',
            'May',
            'June',
            'July',
            'August',
            'September',
            'October',
            'November',
            'December',
        ]
        if 1 <= obj.month <= 12:
            return month_names[obj.month - 1]
        return 'Invalid Month'

    def get_demographics(self, obj):
        # Use aggregated demographics properties
        return obj.demographics_summary


class ModelSettingsSerializer(serializers.ModelSerializer):
    updated_by = UserSerializer(read_only=True)

    class Meta:
        model = ModelSettings
        fields = [
            'id',
            'confidence_threshold_person',
            'confidence_threshold_face',
            'log_interval_seconds',
            'last_updated',
            'updated_by',
        ]

    def validate_confidence_threshold_person(self, value):
        if not 0.0 <= value <= 1.0:
            raise serializers.ValidationError(
                'Person confidence threshold must be between 0.0 and 1.0'
            )
        return value

    def validate_confidence_threshold_face(self, value):
        if not 0.0 <= value <= 1.0:
            raise serializers.ValidationError(
                'Face confidence threshold must be between 0.0 and 1.0'
            )
        return value

    def validate_log_interval_seconds(self, value):
        if value < 1:
            raise serializers.ValidationError('Log interval must be at least 1 second')
        if value > 3600:  # 1 hour
            raise serializers.ValidationError(
                'Log interval cannot exceed 3600 seconds (1 hour)'
            )
        return value


class DetectionDataInputSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    detections = serializers.DictField()

    def validate_detections(self, value):
        male_data = value.get('male')
        female_data = value.get('female')

        if male_data is None or female_data is None:
            raise serializers.ValidationError(
                "Detections must contain 'male' and 'female' keys."
            )

        # Case 1: Detailed age-gender format
        if isinstance(male_data, dict) and isinstance(female_data, dict):
            expected_age_ranges = ['0-9', '10-19', '20-29', '30-39', '40-49', '50+']

            # Check if all expected age ranges are present and are integers
            for age_range in expected_age_ranges:
                if not isinstance(male_data.get(age_range), int):
                    raise serializers.ValidationError(
                        f'Male {age_range} must be an integer.'
                    )
                if not isinstance(female_data.get(age_range), int):
                    raise serializers.ValidationError(
                        f'Female {age_range} must be an integer.'
                    )
            return value  # Valid detailed format

        # Case 2: Simple count format
        elif isinstance(male_data, int) and isinstance(female_data, int):
            return value  # Valid simple count format

        # If neither format matches
        raise serializers.ValidationError(
            "Detections 'male' and 'female' keys must contain either integer "
            "values (for simple counts) or dictionaries with age ranges "
            "(e.g., '0-9', '10-19', etc.) and integer values."
        )
