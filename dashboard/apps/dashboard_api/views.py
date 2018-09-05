from django.contrib.auth.models import User
from rest_framework.decorators import api_view, parser_classes

from .serializers import *
from .models import *
from rest_framework import viewsets, permissions, authentication

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView


class StudentInfoList(viewsets.ReadOnlyModelViewSet):
    queryset = StudentInfo.objects.all()
    serializer_class = StudentInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


@api_view(['POST'])
@parser_classes((JSONParser,))
def student_query_view(request, format=None):
    """
    A view that can accept POST requests with JSON content.
    """
    return Response({'received data': request.data})
