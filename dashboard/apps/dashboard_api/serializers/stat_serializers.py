from rest_framework import serializers
from dashboard.apps.dashboard_api.models.stat_models import *

# ========================================================================= #
# STAT SERIALIZER - Wits performance data                                   #
# ========================================================================= #


# School Info

class SchoolInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolInfo


# Course Info

class CourseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseInfo


# Program Info

class ProgramInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramInfo


# Student Info

class StudentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInfo


# Course Stats

class CourseStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStats


# Progress Description

class ProgressDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressDescription


# Average Year Marks

class AverageYearMarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = AverageYearMarks


# Year Of Study

class YearOfStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = YearOfStudy


# Student Programs

class StudentProgramsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPrograms
