from .serializers import *
from .models import *
from rest_framework import viewsets, permissions


class StudentInfoList(viewsets.ReadOnlyModelViewSet):
    queryset = StudentInfo.objects.all()
    serializer_class = StudentInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
