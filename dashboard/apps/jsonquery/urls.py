from django.urls import path
from dashboard.apps.jsonquery.views import *
from rest_framework import routers


# ViewSets
router = routers.DefaultRouter()
router.register(r'data/faculties', FacultyViewSet)
router.register(r'data/schools', SchoolViewSet)
router.register(r'data/courses', CourseViewSet)
router.register(r'data/programs', ProgramViewSet)
router.register(r'data/outcomes', ProgressOutcomeViewSet)
router.register(r'data/high-schools', SecondarySchoolViewSet)
router.register(r'data/students', StudentViewSet)
router.register(r'data/year-enrollment', EnrolledYearViewSet)
router.register(r'data/course-enrollment', EnrolledCourseViewSet)

# Urls
urlpatterns = [
    *router.urls,
    path('query/faculties', FacultyQuery.as_view()),
    path('query/schools', SchoolQuery.as_view()),
    path('query/courses', CourseQuery.as_view()),
    path('query/programs', ProgramQuery.as_view()),
    path('query/outcomes', ProgressOutcomeQuery.as_view()),
    path('query/high-schools', SecondarySchoolQuery.as_view()),
    path('query/students', StudentQuery.as_view()),
    path('query/year-enrollment', EnrolledYearQuery.as_view()),
    path('query/course-enrollment', EnrolledCourseQuery.as_view()),
]
