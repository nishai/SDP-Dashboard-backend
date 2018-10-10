from rest_framework import viewsets
from dashboard.apps.dashboard_api.serializers.user_serializers import (UserReportSerializer, ReportChartSerializer,
                                                                       ReportChart, UserReport)


class UserReportViewSet(viewsets.ModelViewSet):
    queryset = UserReport.objects.all()
    serializer_class = UserReportSerializer


class ReportChartViewSet(viewsets.ModelViewSet):
    queryset = ReportChart.objects.all()
    serializer_class = ReportChartSerializer
