from rest_framework import viewsets, permissions

from dashboard.apps.dashboard_api.serializers import *


# ========================================================================= #
# STAT VIEWS - Wits performance data                                        #
# ========================================================================= #

# CourseInfo

class CourseInfoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# SchoolInfo

class SchoolInfoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SchoolInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# CourseStats

class CourseStatsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseStatsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)



