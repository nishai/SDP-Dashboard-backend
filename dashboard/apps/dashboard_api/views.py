from django.shortcuts import get_object_or_404
from .serializers import EnrolmentSerializer
from .models import Enrolment
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

#enrolments/
class EnrollmentList(APIView):
    """List enrolled students"""

    def get(self, request):
        """Return a list of all students"""
        enrol = Enrolment.objects.all()
        serializer = EnrolmentSerializer(enrol, many=True)
        return Response(serializer.data)
