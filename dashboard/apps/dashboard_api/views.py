from django.http import JsonResponse
from rest_framework.decorators import parser_classes, api_view
from .serializers import *
from .models import *
from rest_framework import viewsets, permissions, authentication, parsers
from rest_framework import viewsets
from rest_framework.response import Response


class StudentInfoList(viewsets.ReadOnlyModelViewSet):
    queryset = StudentInfo.objects.all()
    serializer_class = StudentInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class RawStudentListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RawStudentModel.objects.order_by("calendar_instance_year", "encrypted_student_no")[:10]
    serializer_class = RawStudentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


@api_view(['GET', 'POST'])
@parser_classes((parsers.JSONParser,))
def student_query_view(request):
    query = request.data
    queryset = RawStudentModel.objects.all()

    if 'filter' in query:
        pass

    if 'group_by' in query:
        pass

    if 'where' in query:
        pass

    if 'order_by' in query:
        order_by = query['order_by']
        # TODO check that order_by belongs in database
        if type(order_by) is str:
            order_by = [order_by]
        if type(order_by) is list:
            queryset = queryset.order_by(*order_by)
        else:
            return JsonResponse({'error': 'order_by invalid'}, status=400)

    if 'top' not in query:
        queryset = queryset[:5]
        # TODO add paging
    else:
        top = query['top']
        if type(top) is int:
            queryset = queryset[:top]
        else:
            return JsonResponse({'error': 'top invalid'}, status=400)

    serializer = RawStudentSerializer(queryset, many=True)
    return Response(serializer.data)
