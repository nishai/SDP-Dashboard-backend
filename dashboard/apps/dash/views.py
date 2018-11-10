from django.http import JsonResponse
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from dashboard.apps.dash.serializers import *
from dashboard.shared.permissions import IsOwner


# ========================================================================= #
# USER VIEWS                                                                #
# ========================================================================= #


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


# ========================================================================= #
# UTIL VIEWS                                                                #
# ========================================================================= #

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@authentication_classes([])
def status_view(request):
    """
    Used to check if the server is alive.
    """
    return JsonResponse({'status': 'active'})
