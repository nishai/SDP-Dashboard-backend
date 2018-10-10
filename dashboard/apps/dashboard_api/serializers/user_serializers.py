
# Serializer for StudentInfo table
from rest_framework import serializers
from dashboard.apps.dashboard_api.models import *


class UserReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReport
        fields = '__all__'


class ReportChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportChart
        fields = '__all__'
