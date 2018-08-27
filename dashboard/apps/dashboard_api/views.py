from .serializers import EnrolmentSerializer
from .models import Enrolment
from rest_framework import viewsets, permissions


class EnrollmentList(viewsets.ReadOnlyModelViewSet):
    queryset = Enrolment.objects.all()
    serializer_class = EnrolmentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
