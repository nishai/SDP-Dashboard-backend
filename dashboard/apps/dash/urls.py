from django.conf.urls import url
from rest_framework import routers
from dashboard.apps.dash.views import *


# ViewSets
router = routers.DefaultRouter()
router.register(r'user', UserReportViewSet)
router.register(r'user/reports', UserReportViewSet)
router.register(r'user/reports/charts', ReportChartViewSet)

# Urls
urlpatterns = [
    *router.urls,
    url(r'^status', status_view),   # Returns an empty body with status code 200 to check that the server is alive.
]
