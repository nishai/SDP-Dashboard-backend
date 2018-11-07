from django.urls import path
from rest_framework import routers
from dashboard.apps.excel_import.views import *

# legacy
router = routers.DefaultRouter()
router.register(r'course_stats', CourseStatsViewSet, base_name="query")
router.register(r'course_info', CourseInfoViewSet, base_name="query")
router.register(r'school_info', SchoolInfoViewSet, base_name="query")
router.register(r'average_year_stats', AverageYearMarksViewSet, base_name="query")

# Urls
urlpatterns = [
    # legacy
    path('course_stats/query', CourseStatsQuery.as_view()),
    path('course_info/query', CourseInfoQuery.as_view()),
    path('school_info/query', SchoolInfoQuery.as_view()),
    path('average_year_stats/query', AverageYearMarksQuery.as_view()),
    # must be at bottom
    *router.urls,
]


