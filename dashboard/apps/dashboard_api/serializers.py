from .models import *
from rest_framework import serializers


class RawStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawStudentModel
        fields = '__all__'

# Serializer for StudentInfo table
class StudentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInfo
        fields = '__all__'


# Serializer for ProgramInfo table
class ProgramInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramInfo
        fields = '__all__'


# Serializer for CourseStats table
class CourseStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStats
        fields = '__all__'


class AverageYearMarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = AverageYearMarks
        fields = '__all__'



class GeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = '__all__'
