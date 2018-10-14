from rest_framework import serializers
from dashboard.apps.dashboard_api.models.wits_models import *

# ========================================================================= #
# WITS SERIALIZER - Wits data                                               #
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
