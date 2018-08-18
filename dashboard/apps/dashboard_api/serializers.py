from .models import Enrolment
from rest_framework import serializers

class EnrolmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrolment
        fields = '__all__'
