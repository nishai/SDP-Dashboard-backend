from pprint import pprint

from django.core.exceptions import FieldError
from django.http import JsonResponse
from jsonschema import ValidationError
from rest_framework.views import APIView

from dashboard.apps.dashboard_api.jsonquery import jsonquery, jsonqueryset
from dashboard.apps.dashboard_api.models import *


# ========================================================================= #
# HELPER                                                                    #
# ========================================================================= #


class QueryApiView(APIView):

    query_model = None
    querier = jsonqueryset

    def _debug_check_fields(self, request, queryset):
        try:
            if len(queryset) > 0:
                try:
                    item = list(queryset[:1])[0]
                except:
                    item = None
                if type(item) is dict:
                    names = tuple(item)
                    fakes = tuple(self.querier.parse_options(self.query_model, request.data))
                    print(
                        f"\n{'=' * 30}\nNAMES vs FAKES - equal: {names == fakes}\nnames: {names}\nfakes: {fakes}\n{'=' * 30}\n")
        except:
            print(f"\n{'=' * 30}\nNAMES vs FAKES - failed\n{'=' * 30}\n")

    def post(self,  request, *args, **kwargs):
        try:
            fake = ('fake' in request.query_params) and (request.query_params['fake'] in ['True', 'true', '1'])
            queryset = self.querier.parse_request(self.query_model, request.data, fake=fake)
            if not fake:
                self._debug_check_fields(request, queryset)
        except ValidationError as e:
            return JsonResponse({"status": "invalid", "message": "json error", "description": str(e)})   # received json is wrong
        except FieldError as e:
            return JsonResponse({"status": "invalid", "message": "field not found", "description": str(e)})   # received field name is wrong / does not exist
        # valid result
        return JsonResponse({"status": "valid", "results": list(queryset)})

    def options(self, request, *args, **kwargs):
        try:
            queryset = self.querier.parse_options(self.query_model, request.data)
        except ValidationError as e:
            return JsonResponse({"status": "invalid", "message": str(e)})   # received json is wrong
        except FieldError as e:
            return JsonResponse({"status": "invalid", "message": str(e)})   # received field name is wrong / does not exist
        # valid result
        return JsonResponse({"status": "valid", "results": list(queryset)})


# ========================================================================= #
# OLD - QUERY VIEWS                                                         #
# ========================================================================= #


# CourseStats

class CourseStatsQuery(QueryApiView):
    query_model = CourseStats
    querier = jsonquery


# SchoolInfo

class SchoolInfoQuery(QueryApiView):
    query_model = SchoolInfo
    querier = jsonquery


# CourseInfo

class CourseInfoQuery(QueryApiView):
    query_model = CourseInfo
    querier = jsonquery


# ========================================================================= #
# NEW - QUERY VIEWS                                                         #
# ========================================================================= #


# Faculty

class FacultyQuery(QueryApiView):
    query_model = Faculty


# School

class SchoolQuery(QueryApiView):
    query_model = School


# Course

class CourseQuery(QueryApiView):
    query_model = Course


# Program

class ProgramQuery(QueryApiView):
    query_model = Program


# Progress

class ProgressOutcomeQuery(QueryApiView):
    query_model = ProgressOutcome


# Secondary School

class SecondarySchoolQuery(QueryApiView):
    query_model = SecondarySchool


# Student

class StudentQuery(QueryApiView):
    query_model = Student


# Enrolled Year

class EnrolledYearQuery(QueryApiView):
    query_model = EnrolledYear


# Enrolled Course

class EnrolledCourseQuery(QueryApiView):
    query_model = EnrolledCourse
