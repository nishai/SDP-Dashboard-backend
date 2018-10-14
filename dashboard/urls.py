"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from dashboard.apps.dashboard_api.views import *
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token


# ========================================================================= #
# ROUTING OBJECTS                                                           #
# ========================================================================= #


# Django
urlpatterns = []

# Django Rest Framework
router = routers.DefaultRouter()


# ========================================================================= #
# APP ROUTES                                                                #
# ========================================================================= #


# Query Views
urlpatterns += [
    path('query/course-stats', course_stats_query),
    path('query/school-info', school_info_query),
    path('query/course-info', course_info_query),
]

# School Info
router.register(r'info/schools', SchoolInfoViewSet)
router.register(r'info/courses', CourseInfoViewSet)
router.register(r'info/programs', ProgramInfoViewSet)
router.register(r'info/students', StudentInfoViewSet)
router.register(r'info/courses-stats', CourseStatsViewSet)
router.register(r'info/outcomes', ProgressDescriptionViewSet)
router.register(r'info/average-year-marks', AverageYearMarksViewSet)
router.register(r'info/year-of-study', YearOfStudyViewSet)
router.register(r'info/student-programs', StudentProgramsViewSet)

# User Viewsets
router.register(r'user', UserReportViewSet)
router.register(r'user/reports', UserReportViewSet)
router.register(r'user/reports/charts', ReportChartViewSet)

# Wits Viewsets
router.register(r'data/faculties', FacultyViewSet)
router.register(r'data/schools', SchoolViewSet)
router.register(r'data/courses', CourseViewSet)
router.register(r'data/programs', ProgramViewSet)
router.register(r'data/outcomes', ProgressOutcomeViewSet)
router.register(r'data/high-schools', SecondarySchoolViewSet)
router.register(r'data/students', StudentViewSet)
router.register(r'data/year-enrollment', EnrolledYearViewSet)
router.register(r'data/course-enrollment', EnrolledCourseViewSet)

# Util Views
urlpatterns += [
    url(r'^status', status_view),   # Returns an empty body with status code 200 to check that the server is alive.
]

# JWT Authentication TODO: THIS IS NOT SECURE UNTIL HTTPS IS USED
# http://getblimp.github.io/django-rest-framework-jwt
urlpatterns += [
    url(r'^auth/token/obtain', obtain_jwt_token),     # obtain a new token from user + pass
    url(r'^auth/token/refresh', refresh_jwt_token),   # obtain a new token from an old token : JWT_ALLOW_REFRESH=True
]


# ========================================================================= #
# DEFAULT ROUTES                                                            #
# ========================================================================= #


# Builtin Django database admin
urlpatterns += [
    path('admin/', admin.site.urls),
]

# api
urlpatterns += [
    url(r'^', include(router.urls)),
]
