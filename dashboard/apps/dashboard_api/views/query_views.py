from django.core.exceptions import FieldError
from django.http import JsonResponse
from jsonschema import ValidationError
from rest_framework.views import APIView

from dashboard.apps.dashboard_api.jsonquery import jsonquery
from dashboard.apps.dashboard_api.models import *


# ========================================================================= #
# HELPER                                                                    #
# ========================================================================= #


class QueryApiView(APIView):

    query_model = None

    def post(self,  request, *args, **kwargs):
        try:
            queryset = jsonquery.parse_request(self.query_model, request.data)
        except ValidationError as e:
            return JsonResponse({"status": "invalid", "message": str(e)})   # received json is wrong
        except FieldError as e:
            return JsonResponse({"status": "invalid", "message": str(e)})   # received field name is wrong / does not exist
        # valid result
        return JsonResponse({"status": "valid", "results": list(queryset)})

    def options(self, request, *args, **kwargs):
        print(request, args, kwargs)
        return JsonResponse({'status': 'active'})


# ========================================================================= #
# QUERY VIEWS                                                               #
# ========================================================================= #


# CourseStats

class CourseStatsQuery(QueryApiView):
    query_model = CourseStats


# SchoolInfo

class SchoolInfoQuery(QueryApiView):
    query_model = SchoolInfo


# CourseInfo

class CourseInfoQuery(QueryApiView):
    query_model = CourseInfo
