from rest_framework import viewsets, permissions
from dashboard.apps.excel_import.parser import jsonquery

from dashboard.apps.excel_import.serializers import *
from dashboard.apps.jsonquery.views import QueryApiView  # TODO: remove


# ========================================================================= #
# OLD - QUERY VIEWS                                                         #
# Legacy Views - TODO: REMOVE                                               #
# ========================================================================= #


# CourseStats

class CourseStatsQuery(QueryApiView):
    query_model = CourseStats
    querier = jsonquery


# SchoolInfo

class SchoolInfoQuery(QueryApiView):
    query_model = SchoolInfo
    querier = jsonquery


# CourseInfo

class CourseInfoQuery(QueryApiView):
    query_model = CourseInfo
    querier = jsonquery


# ========================================================================= #
# STAT VIEWS - Wits performance data                                        #
# Legacy Views - TODO: REMOVE                                               #
# ========================================================================= #


# School Info

class SchoolInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = SchoolInfo.objects.order_by("faculty")
    serializer_class = SchoolInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Course Info

class CourseInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = CourseInfo.objects.order_by("course_code")
    serializer_class = CourseInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Program Info

class ProgramInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = ProgramInfo.objects.order_by("program_code")
    serializer_class = ProgramInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Student Info

class StudentInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = StudentInfo.objects.all()
    serializer_class = StudentInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Course Stats

class CourseStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = CourseStats.objects.order_by("course_code_id", "calendar_instance_year", "encrypted_student_no_id")
    serializer_class = CourseStatsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Progress Description

class ProgressDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = ProgressDescription.objects.order_by("progress_outcome_type")
    serializer_class = ProgressDescriptionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Average Year Marks

class AverageYearMarksViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = AverageYearMarks.objects.all()
    serializer_class = AverageYearMarksSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Year Of Study

class YearOfStudyViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = YearOfStudy.objects.all()
    serializer_class = YearOfStudySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Student Programs

class StudentProgramsViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = StudentPrograms.objects.all()
    serializer_class = StudentProgramsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
