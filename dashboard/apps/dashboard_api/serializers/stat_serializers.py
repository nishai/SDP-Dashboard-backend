from rest_framework import serializers
from dashboard.apps.dashboard_api.models.stat_models import *

# ========================================================================= #
# STAT SERIALIZER - Wits performance data                                   #
# ========================================================================= #


# School Info

class SchoolInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolInfo
        fields = '__all__'


# Course Info

class CourseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseInfo
        fields = '__all__'


# Program Info

class ProgramInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramInfo
        fields = '__all__'


# Student Info

class StudentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInfo
        fields = '__all__'


# Course Stats

class CourseStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStats
        fields = '__all__'


# Progress Description

class ProgressDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressDescription
        fields = '__all__'


# Average Year Marks

class AverageYearMarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = AverageYearMarks
        fields = '__all__'


# Year Of Study

class YearOfStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = YearOfStudy
        fields = '__all__'


# Student Programs

class StudentProgramsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPrograms
        fields = '__all__'
