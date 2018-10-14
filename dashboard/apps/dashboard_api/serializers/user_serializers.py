from rest_framework import serializers
from dashboard.apps.dashboard_api.models.user_models import *

# ========================================================================= #
# USER SERIALIZER                                                           #
# ========================================================================= #


# User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User


# User Report

class UserReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReport


# User Report Charts

class ReportChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportChart
