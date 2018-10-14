from rest_framework import viewsets, permissions, generics
from dashboard.apps.dashboard_api.views.permissions.permissions import IsOwner
from dashboard.apps.dashboard_api.serializers.user_serializers import (UserReportSerializer, ReportChartSerializer,
                                                                       ReportChart, UserReport)


# ========================================================================= #
# USER VIEWS                                                                #
# ========================================================================= #


# User

# TODO

# User Report

class UserReportViewSet(viewsets.ModelViewSet):
    queryset = UserReport.objects.all()
    serializer_class = UserReportSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)


# User Report Charts

class ReportChartViewSet(viewsets.ModelViewSet):
    queryset = ReportChart.objects.all()
    serializer_class = ReportChartSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)
