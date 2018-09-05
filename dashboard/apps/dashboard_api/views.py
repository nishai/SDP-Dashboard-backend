from .serializers import *
from .models import *
from rest_framework import viewsets, permissions, authentication
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response


class StudentInfoList(viewsets.ReadOnlyModelViewSet):
    queryset = StudentInfo.objects.all()
    serializer_class = StudentInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class StudentViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = StudentInfo.objects.all()
        serializer = StudentInfoSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = StudentInfo.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = StudentInfoSerializer(user)
        return Response(serializer.data)
