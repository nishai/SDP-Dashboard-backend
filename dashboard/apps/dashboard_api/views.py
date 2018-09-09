from django.core.exceptions import FieldError
from django.http import JsonResponse
from jsonschema import ValidationError, SchemaError
from rest_framework.decorators import parser_classes, api_view
from dashboard.apps.dashboard_api.jsonquery import jsonquery
from dashboard.apps.dashboard_api.serializers import StudentInfoSerializer, RawStudentSerializer
from .models import *
from rest_framework import permissions, parsers, viewsets


# ========================================================================= #
# VIEWS                                                                     #
# ========================================================================= #


class StudentInfoList(viewsets.ReadOnlyModelViewSet):
    queryset = StudentInfo.objects.all()
    serializer_class = StudentInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class RawStudentListViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Data Structure:
    ---------------
        Encrypted Student No                      =   0021D31BE03E4AB097DCF9C0C89B13BA
        Calendar Instance Year                    =   2013
        Program Code                              =   SB000
        Program Title                             =   Bachelor of  Science
        Year of Study                             =   YOS 2
        Nationality Short Name                    =   South Africa
        Home Language Description                 =   South Sotho
        Race Description                          =   Black
        Gender                                    =   F
        Age                                       =   25
        Course Code                               =   CHEM2003
        Final Mark                                =   50
        Final Grade                               =   PMP
        Progress Outcome Type                     =   PCD
        Progress Outcome Type Description         =   Permitted to proceed
        Award Grade                               =   Q         # used for 3rd years / degree completion
        Average Marks                             =   65,67
        Secondary School Quintile                 =   4
        Urban / Rural Secondary School            =   URBAN
        Secondary School Name                     =   Forte Secondary School
    """
    queryset = RawStudentModel.objects.order_by("calendar_instance_year", "encrypted_student_no")
    serializer_class = RawStudentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# ========================================================================= #
# QUERY VIEW                                                                #
# ========================================================================= #

@api_view(['GET', 'POST'])
@parser_classes((parsers.JSONParser,))
def student_query_view(request):
    try:
        queryset = jsonquery.parse(
            RawStudentModel,
            request.data
        )
    except ValidationError as e:
        return JsonResponse({"status": "invalid", "message": str(e)})
    except FieldError as e:
        return JsonResponse({"status": "invalid", "message":  str(e)})
    return JsonResponse({"status": "valid", "results": list(queryset)})


