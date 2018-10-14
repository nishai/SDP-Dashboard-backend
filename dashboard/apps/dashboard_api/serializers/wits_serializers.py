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


# School

class SchoolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = School


# Course

class CourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Course


# Program

class ProgramSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Program


# Progress

class ProgressOutcomeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProgressOutcome


# Secondary School

class SecondarySchoolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SecondarySchool


# Student

class StudentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Student


# Enrolled Year

class EnrolledYearSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnrolledYear


# Enrolled Course

class EnrolledCourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnrolledCourse
