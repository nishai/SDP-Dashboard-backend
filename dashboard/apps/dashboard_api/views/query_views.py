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

    def post(self,  request, *args, **kwargs):
        try:
            queryset = jsonqueryset.parse_request(self.query_model, request.data)
            try:
                if len(queryset) > 0:
                    item = list(queryset[:1])[0]
                    if type(item) is dict:
                        names = tuple(item)
                        fakes = tuple(jsonqueryset.parse_options(self.query_model, request.data))
                        print(f"\n{'='*30}\nNAMES vs FAKES - equal: {names == fakes}\nnames: {names}\nfakes: {fakes}\n{'='*30}\n")
            except:
                print(f"\n{'=' * 30}\nNAMES vs FAKES - failed\n{'=' * 30}\n")
        except ValidationError as e:
            return JsonResponse({"status": "invalid", "message": str(e)})   # received json is wrong
        except FieldError as e:
            return JsonResponse({"status": "invalid", "message": str(e)})   # received field name is wrong / does not exist
        # valid result
        return JsonResponse({"status": "valid", "results": list(queryset)})

    def options(self, request, *args, **kwargs):
        try:
            queryset = jsonqueryset.parse_options(self.query_model, request.data)
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


# SchoolInfo

class SchoolInfoQuery(QueryApiView):
    query_model = SchoolInfo


# CourseInfo

class CourseInfoQuery(QueryApiView):
    query_model = CourseInfo



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

