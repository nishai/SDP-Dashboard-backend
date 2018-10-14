from rest_framework import viewsets, permissions

from dashboard.apps.dashboard_api.serializers import *


# ========================================================================= #
# WITS VIEWS                                                               #
# ========================================================================= #


# Faculty

class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# School

class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Course

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Program

class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Progress

class ProgressOutcomeViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = ProgressOutcome.objects.all()
    serializer_class = ProgressOutcomeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Secondary School

class SecondarySchoolViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = SecondarySchool.objects.all()
    serializer_class = SecondarySchoolSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Student

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Enrolled Year

class EnrolledYearViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = EnrolledYear.objects.all()
    serializer_class = EnrolledYearSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Enrolled Course

class EnrolledCourseViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = EnrolledCourse.objects.all()
    serializer_class = EnrolledCourseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
