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

router = routers.DefaultRouter()
router.register(r'course_info', CourseInfoViewSet, base_name="query")
router.register(r'school_info', SchoolInfoViewSet, base_name="query")
router.register(r'course_stats', CourseStatsViewSet, base_name="query")

# admin / auth / debug
urlpatterns = [
    # Builtin Django database admin
    path('admin/', admin.site.urls),
    # JWT Authentication Endpoints : http://getblimp.github.io/django-rest-framework-jwt
    # TODO: THIS IS NOT SECURE UNTIL HTTPS IS USED
    url(r'^auth/token/obtain', obtain_jwt_token),     # obtain a new token from user + pass
    url(r'^auth/token/refresh', refresh_jwt_token),   # obtain a new token from an old token : JWT_ALLOW_REFRESH=True
]

# api
urlpatterns += [
    url(r'^', include(router.urls)),
    path('course_stats/query', course_stats_query),
    path('school_info/query', school_info_query),
    path('course_info/query', course_info_query),
]
