from django.urls import path
from rest_framework import routers
from dashboard.apps.excel_import.views import *

# ViewSets
router = routers.DefaultRouter()
router.register(r'info/schools', SchoolInfoViewSet)
router.register(r'info/courses', CourseInfoViewSet)
router.register(r'info/programs', ProgramInfoViewSet)
router.register(r'info/students', StudentInfoViewSet)
router.register(r'info/courses-stats', CourseStatsViewSet)
router.register(r'info/outcomes', ProgressDescriptionViewSet)
router.register(r'info/average-year-marks', AverageYearMarksViewSet)
router.register(r'info/year-of-study', YearOfStudyViewSet)
router.register(r'info/student-programs', StudentProgramsViewSet)

# Urls
urlpatterns = [
    *router.urls,
    path('query/course-stats', CourseStatsQuery.as_view()),
    path('query/school-info', SchoolInfoQuery.as_view()),
    path('query/course-info', CourseInfoQuery.as_view()),
]
