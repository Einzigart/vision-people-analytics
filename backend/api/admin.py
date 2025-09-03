from django.contrib import admin

from .models import (
    DailyAggregation,
    DetectionData,
    # MonthlyAggregation removed
    ModelSettings,
    MonthlyAggregation,
)


@admin.register(DetectionData)
class DetectionDataAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp',
        'get_total_count',
        'get_male_count',
        'get_female_count',
        'is_aggregated',
    )
    list_filter = ('is_aggregated', 'timestamp')
    search_fields = ('timestamp',)
    readonly_fields = (
        'get_male_count',
        'get_female_count',
        'get_total_count',
    )  # These are computed properties
    ordering = ('-timestamp',)

    def get_male_count(self, obj):
        return obj.male_count

    get_male_count.short_description = 'Male Count'

    def get_female_count(self, obj):
        return obj.female_count

    get_female_count.short_description = 'Female Count'

    def get_total_count(self, obj):
        return obj.total_count

    get_total_count.short_description = 'Total Count'

    fieldsets = (
        ('Basic Information', {'fields': ('timestamp', 'is_aggregated')}),
        (
            'Age Group Breakdown - Male',
            {
                'fields': (
                    'male_0_9',
                    'male_10_19',
                    'male_20_29',
                    'male_30_39',
                    'male_40_49',
                    'male_50_plus',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Age Group Breakdown - Female',
            {
                'fields': (
                    'female_0_9',
                    'female_10_19',
                    'female_20_29',
                    'female_30_39',
                    'female_40_49',
                    'female_50_plus',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Computed Totals',
            {
                'fields': ('get_male_count', 'get_female_count', 'get_total_count'),
                'classes': ('collapse',),
            },
        ),
    )


@admin.register(DailyAggregation)
class DailyAggregationAdmin(admin.ModelAdmin):
    list_display = ('date', 'get_total_count', 'get_male_count', 'get_female_count')
    list_filter = ('date',)
    search_fields = ('date',)
    ordering = ('-date',)
    readonly_fields = (
        'get_male_count',
        'get_female_count',
        'get_total_count',
    )  # These are computed properties

    def get_male_count(self, obj):
        return obj.male_count

    get_male_count.short_description = 'Male Count'

    def get_female_count(self, obj):
        return obj.female_count

    get_female_count.short_description = 'Female Count'

    def get_total_count(self, obj):
        return obj.total_count

    get_total_count.short_description = 'Total Count'

    fieldsets = (
        ('Basic Information', {'fields': ('date',)}),
        (
            'Age Group Breakdown - Male',
            {
                'fields': (
                    'male_0_9',
                    'male_10_19',
                    'male_20_29',
                    'male_30_39',
                    'male_40_49',
                    'male_50_plus',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Age Group Breakdown - Female',
            {
                'fields': (
                    'female_0_9',
                    'female_10_19',
                    'female_20_29',
                    'female_30_39',
                    'female_40_49',
                    'female_50_plus',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Computed Totals',
            {
                'fields': (
                    'get_male_count',
                    'get_female_count',
                    'get_total_count',
                ),  # These are computed properties
                'classes': ('collapse',),
            },
        ),
    )


@admin.register(MonthlyAggregation)
class MonthlyAggregationAdmin(admin.ModelAdmin):
    list_display = (
        'year',
        'month',
        'month_display',
        'get_total_count',
        'get_male_count',
        'get_female_count',
    )
    list_filter = ('year', 'month')
    search_fields = ('year', 'month')
    readonly_fields = (
        'get_male_count',
        'get_female_count',
        'get_total_count',
        'get_total_male',
        'get_total_female',
    )  # These are computed properties
    ordering = ('-year', '-month')

    def month_display(self, obj):
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
        return f'Month {obj.month}'

    month_display.short_description = 'Month Name'

    def get_male_count(self, obj):
        return obj.male_count

    get_male_count.short_description = 'Male Count'

    def get_female_count(self, obj):
        return obj.female_count

    get_female_count.short_description = 'Female Count'

    def get_total_count(self, obj):
        return obj.total_count

    get_total_count.short_description = 'Total Count'

    def get_total_male(self, obj):
        return obj.total_male

    get_total_male.short_description = 'Total Male (Legacy)'

    def get_total_female(self, obj):
        return obj.total_female

    get_total_female.short_description = 'Total Female (Legacy)'

    fieldsets = (
        ('Basic Information', {'fields': ('year', 'month')}),
        (
            'Age Group Breakdown - Male',
            {
                'fields': (
                    'male_0_9',
                    'male_10_19',
                    'male_20_29',
                    'male_30_39',
                    'male_40_49',
                    'male_50_plus',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Age Group Breakdown - Female',
            {
                'fields': (
                    'female_0_9',
                    'female_10_19',
                    'female_20_29',
                    'female_30_39',
                    'female_40_49',
                    'female_50_plus',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Computed Totals',
            {
                'fields': (
                    'get_male_count',
                    'get_female_count',
                    'get_total_count',
                    'get_total_male',
                    'get_total_female',
                ),
                'classes': ('collapse',),
            },
        ),
    )


# MonthlyAggregationAdmin is not needed as the model is removed.


@admin.register(ModelSettings)
class ModelSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'confidence_threshold_person',
        'confidence_threshold_face',
        'log_interval_seconds',
        'last_updated',
        'updated_by',
    )
    readonly_fields = ('last_updated',)

    fieldsets = (
        (
            'Detection Thresholds',
            {'fields': ('confidence_threshold_person', 'confidence_threshold_face')},
        ),
        ('Logging Configuration', {'fields': ('log_interval_seconds',)}),
        (
            'Metadata',
            {'fields': ('last_updated', 'updated_by'), 'classes': ('collapse',)},
        ),
    )

    def has_add_permission(self, request):
        # Only allow one settings record
        return not ModelSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False


# If MonthlyAggregation was previously registered, ensure it's unregistered.
# For now, since it wasn't explicitly registered in the provided file,
# we don't need to do anything additional.
