from rest_framework import serializers
from dashboard.apps.wits.models import *


# ========================================================================= #
# WITS SERIALIZERS - Wits data                                              #
# https://www.django-rest-framework.org/api-guide/serializers               #
# ========================================================================= #


# Faculty

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = '__all__'


# School

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'


# Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


# Program

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'


# Progress

class ProgressOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressOutcome
        fields = '__all__'


# Secondary School

class SecondarySchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondarySchool
        fields = '__all__'


# Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


# Enrolled Year

class EnrolledYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrolledYear
        fields = '__all__'


# Enrolled Course

class EnrolledCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrolledCourse
        fields = '__all__'
