from django.core.exceptions import FieldError
from django.http import JsonResponse
from jsonschema import ValidationError
from rest_framework.views import APIView

from dashboard.apps.jsonquery.parser import jsonqueryset
from dashboard.apps.jsonquery.serializers import *


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
                    fakes = tuple(self.querier.parse_request(self.query_model, request.data, fake=True))
                    print(
                        f"\n{'=' * 30}\nNAMES vs FAKES - equal: {names == fakes}\nnames: {names}\nfakes: {fakes}\n{'=' * 30}\n")
        except:
            print(f"\n{'=' * 30}\nNAMES vs FAKES - failed\n{'=' * 30}\n")

    def post(self,  request, *args, **kwargs):
        try:
            fake = ('fake' in request.query_params) and (request.query_params['fake'] in ['True', 'true', '1'])
            queryset = self.querier.parse_request(self.query_model, request.data, fake=fake)
            if not fake: # check that fields are the same, for debugging purposes
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


# ========================================================================= #
# WITS VIEWS                                                                #
# ========================================================================= #


# Faculty

class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# School

class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Course

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Program

class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Progress

class ProgressOutcomeViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = ProgressOutcome.objects.all()
    serializer_class = ProgressOutcomeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Secondary School

class SecondarySchoolViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = SecondarySchool.objects.all()
    serializer_class = SecondarySchoolSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Student

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Enrolled Year

class EnrolledYearViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = EnrolledYear.objects.all()
    serializer_class = EnrolledYearSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


# Enrolled Course

class EnrolledCourseViewSet(viewsets.ReadOnlyModelViewSet):
    """ `list` and `detail` actions. """
    queryset = EnrolledCourse.objects.all()
    serializer_class = EnrolledCourseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )