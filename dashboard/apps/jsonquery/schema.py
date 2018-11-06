from graphene import relay
import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from dashboard.apps.jsonquery.models import *


# ========================================================================= #
# GRAPHQL TYPES                                                             #
# ========================================================================= #


# Faculty

class FacultyType(DjangoObjectType):
    class Meta:
        model = Faculty
        interfaces = (relay.Node,)
        filter_fields = {'faculty_title': ['contains', 'icontains', 'exact', 'iexact', 'startswith', 'istartswith', 'endswith', 'iendswith']}


# School

class SchoolType(DjangoObjectType):
    class Meta:
        model = School
        interfaces = (relay.Node,)
        filter_fields = []


# Course

class CourseType(DjangoObjectType):
    class Meta:
        model = Course
        interfaces = (relay.Node,)
        filter_fields = []


# Program

class ProgramType(DjangoObjectType):
    class Meta:
        model = Program
        interfaces = (relay.Node,)
        filter_fields = []


# Progress

class ProgressOutcomeType(DjangoObjectType):
    class Meta:
        model = ProgressOutcome
        interfaces = (relay.Node,)
        filter_fields = []


# Secondary School

class SecondarySchoolType(DjangoObjectType):
    class Meta:
        model = SecondarySchool
        interfaces = (relay.Node,)
        filter_fields = []


# Student

class StudentType(DjangoObjectType):
    class Meta:
        model = Student
        interfaces = (relay.Node,)
        filter_fields = []


# Enrolled Year

class EnrolledYearType(DjangoObjectType):
    class Meta:
        model = EnrolledYear
        interfaces = (relay.Node,)
        filter_fields = []


# Enrolled Course

class EnrolledCourseType(DjangoObjectType):
    class Meta:
        model = EnrolledCourse
        interfaces = (relay.Node,)
        filter_fields = []


# ========================================================================= #
# GRAPHQL SCHEMA                                                            #
# ========================================================================= #


def get(dictionary: dict, *keys: str):
    return tuple(dictionary.get(key) for key in keys)


class WitsQuerySchema(object):

    faculty = relay.Node.Field(FacultyType)
    all_faculties = DjangoFilterConnectionField(FacultyType)

    school = relay.Node.Field(SchoolType)
    all_schools = DjangoFilterConnectionField(SchoolType)

    course = relay.Node.Field(CourseType)
    all_courses = DjangoFilterConnectionField(CourseType)

    program = relay.Node.Field(ProgramType)
    all_programs = DjangoFilterConnectionField(ProgramType)

    progress_outcome = relay.Node.Field(ProgressOutcomeType)
    all_progress_outcomes = DjangoFilterConnectionField(ProgressOutcomeType)

    secondary_school = relay.Node.Field(SecondarySchoolType)
    all_secondary_schools = DjangoFilterConnectionField(SecondarySchoolType)

    student = relay.Node.Field(StudentType)
    all_students = DjangoFilterConnectionField(StudentType)

    enrolled_year = relay.Node.Field(EnrolledYearType)
    all_enrolled_years = DjangoFilterConnectionField(EnrolledYearType)

    enrolled_course = relay.Node.Field(EnrolledCourseType)
    all_enrolled_courses = DjangoFilterConnectionField(EnrolledCourseType)

    # all_faculties = graphene.List(FacultyType)
    # all_schools = graphene.List(SchoolType)
    # all_courses = graphene.List(CourseType)
    # all_programs = graphene.List(ProgramType)
    # all_progress_outcomes = graphene.List(ProgressOutcomeType)
    # all_secondary_schools = graphene.List(SecondarySchoolType)
    # all_students = graphene.List(StudentType)
    # all_enrolled_years = graphene.List(EnrolledYearType)
    # all_enrolled_courses = graphene.List(EnrolledCourseType)
    #
    # def resolve_all_faculties(self, info, **kwargs):
    #     return Faculty.objects.all()
    #
    # def resolve_all_schools(self, info, **kwargs):
    #     return School.objects.all()
    #
    # def resolve_all_courses(self, info, **kwargs):
    #     return Course.objects.all()
    #
    # def resolve_all_programs(self, info, **kwargs):
    #     return Program.objects.all()
    #
    # def resolve_all_progress_outcomes(self, info, **kwargs):
    #     return ProgressOutcome.objects.all()
    #
    # def resolve_all_secondary_schools(self, info, **kwargs):
    #     return SecondarySchool.objects.all()
    #
    # def resolve_all_students(self, info, **kwargs):
    #     return Student.objects.all()
    #
    # def resolve_all_enrolled_years(self, info, **kwargs):
    #     return EnrolledYear.objects.all()
    #
    # def resolve_all_enrolled_courses(self, info, **kwargs):
    #     return EnrolledCourse.objects.all()
    #
    # faculty = graphene.Field(FacultyType, id=graphene.Int(), title=graphene.String())
    # school = graphene.Field(SchoolType, id=graphene.Int(), title=graphene.String())
    # course = graphene.Field(CourseType, code=graphene.String())
    # program = graphene.Field(ProgramType, code=graphene.String(), title=graphene.String())
    # progress_outcome = graphene.Field(ProgressOutcomeType, code=graphene.String())
    # secondary_school = graphene.Field(SecondarySchoolType, name=graphene.String())
    # student = graphene.Field(StudentType, student_no=graphene.String())
    # enrolled_year = graphene.Field(EnrolledYearType, id=graphene.Int(), student_no=graphene.String(), program_code=graphene.String(), year=graphene.Int())
    # enrolled_course = graphene.Field(EnrolledCourseType, id=graphene.Int(), course_code=graphene.String(), student_no=graphene.String(), program_code=graphene.String(), year=graphene.Int())
    #
    # def resolve_faculty(self, info, **kwargs):
    #     id, title = get(kwargs, 'id', 'title')
    #     if id is not None:
    #         return Faculty.objects.get(faculty_id=id)
    #     if title is not None:
    #         return Faculty.objects.get(faculty_title=title)
    #     return None
    #
    # def resolve_school(self, info, **kwargs):
    #     id, title = get(kwargs, 'id', 'title')
    #     if id is not None:
    #         return School.objects.get(school_id=id)
    #     if title is not None:
    #         return School.objects.get(school_title=title)
    #     return None
    #
    # def resolve_course(self, info, **kwargs):
    #     code = get(kwargs, 'code')
    #     if code is not None:
    #         return Course.objects.get(course_code=code.upper())
    #     return None
    #
    # def resolve_program(self, info, **kwargs):
    #     code, title = get(kwargs, 'code', 'title')
    #     if code is not None:
    #         return Program.objects.get(program_code=code.upper())
    #     if title is not None:
    #         return Program.objects.get(program_title=title)
    #     return None
    #
    # def resolve_progress_outcome(self, info, **kwargs):
    #     code = get(kwargs, 'code')
    #     if code is not None:
    #         return ProgressOutcome.objects.get(progress_outcome_type=code.upper())
    #     return None
    #
    # def resolve_secondary_school(self, info, **kwargs):
    #     name = get(kwargs, 'name')
    #     if name is not None:
    #         return SecondarySchool.objects.get(secondary_school_name=name)
    #     return None
    #
    # def resolve_student(self, info, **kwargs):
    #     student_no = get(kwargs, 'student_no')
    #     if student_no is not None:
    #         return SecondarySchool.objects.get(encrypted_student_no=student_no)
    #     return None
    #
    # def resolve_enrolled_year(self, info, **kwargs):
    #     id, student_no, program_code, year = get(kwargs, 'id', 'student_no', 'program_code', 'year')
    #     if id is not None:
    #         return EnrolledYear.objects.get(id=id)
    #     if all(val is not None for val in [student_no, program_code, year]):
    #         return EnrolledYear.objects.get(encrypted_student_no=student_no, program_code=program_code.upper(), calendar_instance_year=year)
    #     return None
    #
    # def resolve_enrolled_course(self, info, **kwargs):
    #     id, course_code, student_no, program_code, year = get(kwargs, 'id', 'course_code', 'student_no', 'program_code', 'year')
    #     if id is not None:
    #         return EnrolledCourse.objects.get(id=id)
    #     if all(val is not None for val in [course_code, student_no, program_code, year]):
    #         return EnrolledCourse.objects.get(course_code=course_code.upper(), enrolled_year_id__encrypted_student_no=student_no, enrolled_year_id__program_code=program_code.upper(), enrolled_year_id__calendar_instance_year=year)
    #     return None
