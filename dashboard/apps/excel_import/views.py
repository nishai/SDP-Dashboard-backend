from rest_framework import viewsets, permissions
from dashboard.apps.excel_import.parser import jsonquery

from dashboard.apps.excel_import.serializers import *
from dashboard.apps.jsonquery.views import QueryApiView  # TODO: remove
from dashboard.shared.middleware import WARN_view_deprecated


# ========================================================================= #
# OLD - QUERY VIEWS                                                         #
# Legacy Views - TODO: REMOVE                                               #
# ========================================================================= #


# CourseStats

@WARN_view_deprecated
class CourseStatsQuery(QueryApiView):
    query_model = CourseStats
    querier = jsonquery


# SchoolInfo

@WARN_view_deprecated
class SchoolInfoQuery(QueryApiView):
    query_model = SchoolInfo
    querier = jsonquery


# CourseInfo

@WARN_view_deprecated
class CourseInfoQuery(QueryApiView):
    query_model = CourseInfo
    querier = jsonquery


# AverageYearMarks

@WARN_view_deprecated
class AverageYearMarksQuery(QueryApiView):
    query_model = AverageYearMarks
    querier = jsonquery


# ========================================================================= #
# STAT VIEWS - Wits performance data                                        #
# Legacy Views - TODO: REMOVE                                               #
# ========================================================================= #


# School Info

@WARN_view_deprecated
class SchoolInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = SchoolInfo.objects.order_by("faculty")
    serializer_class = SchoolInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Course Info

@WARN_view_deprecated
class CourseInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = CourseInfo.objects.order_by("course_code")
    serializer_class = CourseInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Program Info

@WARN_view_deprecated
class ProgramInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = ProgramInfo.objects.order_by("program_code")
    serializer_class = ProgramInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Student Info

@WARN_view_deprecated
class StudentInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = StudentInfo.objects.all()
    serializer_class = StudentInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Course Stats

@WARN_view_deprecated
class CourseStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = CourseStats.objects.order_by("course_code_id", "calendar_instance_year", "encrypted_student_no_id")
    serializer_class = CourseStatsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Progress Description

@WARN_view_deprecated
class ProgressDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = ProgressDescription.objects.order_by("progress_outcome_type")
    serializer_class = ProgressDescriptionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Average Year Marks

@WARN_view_deprecated
class AverageYearMarksViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = AverageYearMarks.objects.order_by("progress_outcome_type")
    serializer_class = AverageYearMarksSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Year Of Study

@WARN_view_deprecated
class YearOfStudyViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = YearOfStudy.objects.all()
    serializer_class = YearOfStudySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Student Programs

@WARN_view_deprecated
class StudentProgramsViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = StudentPrograms.objects.all()
    serializer_class = StudentProgramsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
