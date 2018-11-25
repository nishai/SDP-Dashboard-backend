from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from dashboard.apps.dash.models import *

# ========================================================================= #
# USER SERIALIZER                                                           #
# ========================================================================= #

# # User Report Charts
#
# class ReportChartSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = ReportChart
#         fields = '__all__'
#
#
# # User Report
#
# class UserReportSerializer(serializers.ModelSerializer):
#     charts = ReportChartSerializer(many=True)
#
#     class Meta:
#         model = UserReport
#         fields = '__all__'


# Profile

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = (
            'date_created',
            'date_modified',
            'rawData',
        )


# User

class UserSerializer(WritableNestedModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "date_joined",
            # Other
            'profile',
        )



