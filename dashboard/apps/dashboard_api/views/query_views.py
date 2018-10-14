from typing import Type

from django.core.exceptions import FieldError
from django.db.models import Model
from django.http import JsonResponse
from jsonschema import ValidationError
from rest_framework.decorators import parser_classes, api_view

from dashboard.apps.dashboard_api.jsonquery import jsonquery
from dashboard.apps.dashboard_api.models import *
from rest_framework import parsers


# ========================================================================= #
# HELPER                                                                    #
# ========================================================================= #


def _perform_query(model: Type[Model], request):
    try:
        queryset = jsonquery.parse(
            model,
            request.data
        )
    except ValidationError as e:
        return JsonResponse({"status": "invalid", "message": str(e)})
    except FieldError as e:
        return JsonResponse({"status": "invalid", "message": str(e)})

    return JsonResponse({"status": "valid", "results": list(queryset)})


# ========================================================================= #
# QUERY VIEWS                                                               #
# ========================================================================= #


# CourseStats

@api_view(['GET', 'POST'])  # TODO: add OPTIONS support to retrieve possible options for the request
@parser_classes((parsers.JSONParser,))
def course_stats_query(request):
    return _perform_query(CourseStats, request)


# SchoolInfo

@api_view(['GET', 'POST'])  # TODO: add OPTIONS support to retrieve possible options for the request
@parser_classes((parsers.JSONParser,))
def school_info_query(request):
    return _perform_query(SchoolInfo, request)


# CourseInfo

@api_view(['GET', 'POST'])  # TODO: add OPTIONS support to retrieve possible options for the request
@parser_classes((parsers.JSONParser,))
def course_info_query(request):
    return _perform_query(CourseInfo, request)
