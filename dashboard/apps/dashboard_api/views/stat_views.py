from rest_framework import viewsets, permissions

from dashboard.apps.dashboard_api.serializers import *


# ========================================================================= #
# STAT VIEWS - Wits performance data                                        #
# ========================================================================= #

# CourseInfo

class CourseInfoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourseInfo.objects.order_by("course_code")
    serializer_class = CourseInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# SchoolInfo

class SchoolInfoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourseInfo.objects.order_by("faculty")
    serializer_class = SchoolInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# CourseStats

class CourseStatsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourseStats.objects.order_by("course_code_id", "calendar_instance_year", "encrypted_student_no_id")
    serializer_class = CourseStatsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)



