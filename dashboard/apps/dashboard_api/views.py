from django.core.exceptions import FieldError
from django.http import JsonResponse
from jsonschema import ValidationError
from rest_framework.decorators import parser_classes, api_view

from dashboard.apps.dashboard_api.jsonquery import jsonquery
from dashboard.apps.dashboard_api.serializers import *
from .models import *
from rest_framework import permissions, parsers, viewsets


# ========================================================================= #
# VIEWS                                                                     #
# ========================================================================= #

class CourseInfoViewSet(viewsets.ReadOnlyModelViewSet):
#    queryset = CourseInfo.objects.order_by("course_code")
    serializer_class = CourseInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class SchoolInfoViewSet(viewsets.ReadOnlyModelViewSet):
#    queryset = CourseInfo.objects.order_by("faculty")
    serializer_class = SchoolInfoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class CourseStatsViewSet(viewsets.ReadOnlyModelViewSet):
#    queryset = CourseStats.objects.order_by("course_code_id", "calendar_instance_year", "encrypted_student_no_id")
    serializer_class = CourseStatsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


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
# ========================================================================= #
# QUERY VIEW                                                                #
# ========================================================================= #

# {
# 	"chain": [
# 		{
# 			"filter": [
# 				{
# 					"field": "year_of_study",
# 					"operator": "startswith",
# 					"value": "YOS 1",
# 					"exclude": false
# 				}
# 			],
# 			"group": {
# 				"by": [
# 					"age",
# 					"year_of_study"
# 				],
# 				"yield": [
# 					{
# 						"name": "ave",
# 						"via": "ave",
# 						"from": "average_marks"
# 					},
# 					{
# 						"name": "count",
# 						"via": "count",
# 						"from": "age"
# 					}
# 				]
# 			},
# 			"order": [
# 				{
# 					"field": "age",
# 					"descending": false
# 				}
# 			]
# 		}
# 	],
# 	"limit": {
# 		"type": "first",
# 		"num": 1000
# 	}
# }


@api_view(['GET', 'POST'])
@parser_classes((parsers.JSONParser,))
def course_stats_query(request):
    try:
        queryset = jsonquery.parse(
            CourseStats,
            request.data
        )
    except ValidationError as e:
        return JsonResponse({"status": "invalid", "message": str(e)})
    except FieldError as e:
        return JsonResponse({"status": "invalid", "message":  str(e)})

    return JsonResponse({"status": "valid", "results": list(queryset)})

@api_view(['GET', 'POST'])
@parser_classes((parsers.JSONParser,))
def school_info_query(request):
    try:
        queryset = jsonquery.parse(
            SchoolInfo,
            request.data
        )
    except ValidationError as e:
        return JsonResponse({"status": "invalid", "message": str(e)})
    except FieldError as e:
        return JsonResponse({"status": "invalid", "message":  str(e)})

    return JsonResponse({"status": "valid", "results": list(queryset)})

@api_view(['GET', 'POST'])
@parser_classes((parsers.JSONParser,))
def course_info_query(request):
    try:
        queryset = jsonquery.parse(
            CourseInfo,
            request.data
        )
    except ValidationError as e:
        return JsonResponse({"status": "invalid", "message": str(e)})
    except FieldError as e:
        return JsonResponse({"status": "invalid", "message":  str(e)})

    return JsonResponse({"status": "valid", "results": list(queryset)})
