from django.shortcuts import render
from .serializers import EnrolmentSerializer
from .models import Enrolment
from rest_framework import generics

class EnrolmentView(generics.ListCreateAPIView):
    """API endpoint that allows Enrolment data to be viewed/edited"""
    queryset = Enrolment.objects.all()
    serializer_class = EnrolmentSerializer
