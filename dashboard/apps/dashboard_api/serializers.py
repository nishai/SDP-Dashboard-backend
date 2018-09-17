from .models import *
from rest_framework import serializers

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

# Serializer for AverageYearMarks table
class AverageYearMarksSerializer(serializers.ModelSerializer):
	class Meta:
		model = AverageYearMarks
		fields = '__all__'

# Serializer for StudentPrograms table
class StudentProgramsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPrograms
        fields = '__all__'

# Serializer for YearOfStudy table
class YearOfStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = YearOfStudy
        fields = '__all__'

# Serializer for ProgressDiscription table
class ProgressDiscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressDiscription
        fields = '__all__'
