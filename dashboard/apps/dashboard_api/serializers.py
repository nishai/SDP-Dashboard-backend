from .models import *
from rest_framework import serializers

class StudentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInfo
        fields = '__all__'

class ProgramInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramInfo
        fields = '__all__'

class CourseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseInfo
        fields = '__all__'

class CourseStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStats
        fields = '__all__'
