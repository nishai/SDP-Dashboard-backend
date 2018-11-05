from rest_framework import serializers, viewsets, permissions
from dashboard.apps.jsonquery.models import *


# ========================================================================= #
# WITS SERIALIZERS - Wits data                                              #
# https://www.django-rest-framework.org/api-guide/serializers               #
# ========================================================================= #


# Faculty

class FacultySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Faculty
        fields = '__all__'


# School

class SchoolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = School
        fields = '__all__'


# Course

class CourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


# Program

class ProgramSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'


# Progress

class ProgressOutcomeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProgressOutcome
        fields = '__all__'


# Secondary School

class SecondarySchoolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SecondarySchool
        fields = '__all__'


# Student

class StudentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


# Enrolled Year

class EnrolledYearSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnrolledYear
        fields = '__all__'


# Enrolled Course

class EnrolledCourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnrolledCourse
        fields = '__all__'


# ========================================================================= #
# WITS VIEWS                                                                #
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
