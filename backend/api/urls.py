from django.urls import path

from . import views

urlpatterns = [
    path('', views.api_overview, name='api-overview'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('detections/', views.DetectionDataAPIView.as_view(), name='detection-logs'),
    path(
        'daily/', views.DailyAggregationAPIView.as_view(), name='daily-aggregation'
    ),  # Handles age/gender
    # path('daily-age-gender/', views.DailyAgeGenderAggregationAPIView.as_view(),
    # name='daily-age-gender-aggregation'),
    path(
        'monthly/',
        views.MonthlyAggregationAPIView.as_view(),
        name='monthly-aggregation',
    ),  # Handles age/gender
    # NEW CONSOLIDATED ENDPOINTS
    path(
        'stats/today/',
        views.ConsolidatedTodayStatsAPIView.as_view(),
        name='consolidated-today-stats',
    ),
    path(
        'stats/range/<str:start_date>/<str:end_date>/',
        views.ConsolidatedRangeStatsAPIView.as_view(),
        name='consolidated-range-stats',
    ),
    # LEGACY ENDPOINTS (for backward compatibility - will be removed in future)
    path('today/', views.TodayStatsAPIView.as_view(), name='today-stats'),
    path(
        'today-age-gender/',
        views.TodayAgeGenderStatsAPIView.as_view(),
        name='today-age-gender-stats',
    ),
    path(
        'range/<str:start_date>/<str:end_date>/',
        views.DateRangeStatsAPIView.as_view(),
        name='date-range',
    ),
    path(
        'age-gender-range/<str:start_date>/<str:end_date>/',
        views.AgeGenderDateRangeStatsAPIView.as_view(),
        name='age-gender-date-range',
    ),
    path('settings/', views.ModelSettingsAPIView.as_view(), name='model-settings'),
    path(
        'public-settings/',
        views.PublicModelSettingsAPIView.as_view(),
        name='public-model-settings',
    ),
    # Performance monitoring endpoint
    path(
        'performance/',
        views.PerformanceStatsAPIView.as_view(),
        name='performance-stats',
    ),
    # Health check endpoint
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path(
        'trigger-aggregation/',
        views.TriggerAggregationAPIView.as_view(),
        name='trigger-aggregation',
    ),
]
