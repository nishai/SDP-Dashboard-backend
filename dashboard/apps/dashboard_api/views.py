from django.shortcuts import get_object_or_404
from .serializers import *
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

#enrolments/
class StudentInfoList(APIView):
    """List enrolled students"""

    def get(self, request):
        """Return a list of all students"""
        enrol = StudentInfo.objects.all()
        serializer = StudentInfoSerializer(enrol, many=True)
        return Response(serializer.data)
