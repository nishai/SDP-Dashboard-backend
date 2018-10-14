from rest_framework import serializers
from dashboard.apps.dashboard_api.models.user_models import *

# ========================================================================= #
# USER SERIALIZER                                                           #
# ========================================================================= #


# User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


# User Report

class UserReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReport
        fields = '__all__'


# User Report Charts

class ReportChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportChart
        fields = '__all__'
