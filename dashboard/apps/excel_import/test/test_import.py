# ========================================================================= #
# Django pytest Documentation:                                              #
#     - https://pytest-django.readthedocs.io/en/latest/helpers.html         #
#                                                                           #
# Functions that start with "test_" are pytest tests.                       #
#   - 'Arguments' to test functions are called fixtures and are generated   #
#     by pytest on the fly based on their name.                             #
#   - You can define a new fixture by annotating a function with            #
#     @pytest.fixture (The name of the func corresponds to args in a test)  #
#   - Default fixtures are defined by django-pytest... see the link above   #
# ========================================================================= #

from typing import Type

from django.db.models import Model
from django.test import TestCase
from django.core.management import call_command
from dashboard.apps.excel_import.models import *

from decimal import Decimal


# ========================================================================= #
# Helper Functions                                                          #
# ========================================================================= #


def retrieve(model: Type[Model], **filter_args):
    first = model.objects.filter(**filter_args).values().first()
    del first['id']
    return first


# ========================================================================= #
# STAT TESTS - Wits performance data                                        #
# Legacy Tests - TODO: REMOVE                                               #
# ========================================================================= #


class ExcelImportTestCase(TestCase):

    def setUp(self):
        pass

    # test excel_import custom command with provided files
    def test_specific_excel(self):
        self.assertEqual(
            call_command('excel_import', *['--file=a_test_schools.xlsx', '--test'], **{}),
            0
        )

        self.assertEqual(
            call_command('excel_import', *['--file=b_test_db1.xlsx', '--test'], **{}),
            0
        )

        self.assertEqual(
            retrieve(StudentInfo, pk="0008F0850D5A573D93162E7F14E46BD1"),
            {'encrypted_student_no': '0008F0850D5A573D93162E7F14E46BD1', 'nationality_short_name': 'South Africa', 'home_language_description': 'Setswana', 'race_description': 'Black', 'gender': 'X', 'age': 29, 'secondary_school_quintile': '3', 'urban_rural_secondary_school': 'URBAN', 'secondary_school_name': 'Phahama Senior School'}
        )

        self.assertEqual(
            retrieve(CourseStats, encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1", course_code="ENGL1001", calendar_instance_year="2014"),
            {'id': 1, 'course_code_id': 'ENGL1001', 'calendar_instance_year': '2014', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'final_mark': Decimal('55.000'), 'final_grade': 'PAS'}
        )

        self.assertEqual(
            retrieve(AverageYearMarks, encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1", calendar_instance_year="2014"),
            {'id': 1, 'calendar_instance_year': '2014', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'average_marks': Decimal('56.500'), 'progress_outcome_type_id': 'PCD', 'award_grade': None}
        )

        self.assertEqual(
            retrieve(ProgramInfo, pk="AB000"),
            {'program_code': 'AB000', 'program_title': 'Bachelor of Arts'}
        )

        self.assertEqual(
            retrieve(StudentPrograms, calendar_instance_year='2014', program_code="AB000", encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1"),
            {'id': 1, 'calendar_instance_year': '2014', 'program_code_id': 'AB000', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'degree_complete': False}
        )

        self.assertEqual(
            retrieve(ProgressDescription, progress_outcome_type="PCD"),
            {'progress_outcome_type': 'PCD', 'progress_outcome_type_description': 'Permitted to proceed'}
        )

    # test excel_import custom command without providing files
    # i.e. test importing all files in files directory
    def test_multiple_excel(self):
        self.assertEqual(
            call_command('excel_import', *['--file=', '--test'], **{}),
            "-1"
        )

        # asserts for first file
        self.assertEqual(
            retrieve(StudentInfo, pk="0008F0850D5A573D93162E7F14E46BD1"),
            {'encrypted_student_no': '0008F0850D5A573D93162E7F14E46BD1', 'nationality_short_name': 'South Africa', 'home_language_description': 'Setswana', 'race_description': 'Black', 'gender': 'X', 'age': 29, 'secondary_school_quintile': '3', 'urban_rural_secondary_school': 'URBAN', 'secondary_school_name': 'Phahama Senior School'}
        )

        self.assertEqual(
            retrieve(CourseStats, encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1", course_code="ENGL1001", calendar_instance_year="2014"),
            {'course_code_id': 'ENGL1001', 'calendar_instance_year': '2014', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'final_mark': Decimal('55.000'), 'final_grade': 'PAS'}
        )

        self.assertEqual(
            retrieve(AverageYearMarks, encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1", calendar_instance_year="2014"),
            {'calendar_instance_year': '2014', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'average_marks': Decimal('56.500'), 'progress_outcome_type_id': 'PCD', 'award_grade': None}
        )

        self.assertEqual(
            retrieve(ProgramInfo, pk="AB000"),
            {'program_code': 'AB000', 'program_title': 'Bachelor of Arts'})

        self.assertEqual(
            retrieve(StudentPrograms, calendar_instance_year='2014', program_code="AB000", encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1"),
            {'calendar_instance_year': '2014', 'program_code_id': 'AB000', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'degree_complete': False}
        )

        # asserts for second file
        self.assertEqual(
            retrieve(StudentInfo, pk="1234QWERASDFZXCV5687TYIUGHKJBNML"),
            {'encrypted_student_no': '1234QWERASDFZXCV5687TYIUGHKJBNML', 'nationality_short_name': 'South Africa', 'home_language_description': 'Setswana', 'race_description': 'Black', 'gender': 'G', 'age': 29, 'secondary_school_quintile': '3', 'urban_rural_secondary_school': 'URBAN', 'secondary_school_name': 'Phahama Senior School'}
        )

        self.assertEqual(
            retrieve(CourseStats, encrypted_student_no="1234QWERASDFZXCV5687TYIUGHKJBNML", course_code="ENGL1001", calendar_instance_year="1234"),
            {'course_code_id': 'ENGL1001', 'calendar_instance_year': '1234', 'encrypted_student_no_id': '1234QWERASDFZXCV5687TYIUGHKJBNML', 'final_mark': Decimal('55.000'), 'final_grade': 'PAS'}
        )

        self.assertEqual(
            retrieve(AverageYearMarks, encrypted_student_no="1234QWERASDFZXCV5687TYIUGHKJBNML", calendar_instance_year="1234"),
            {'calendar_instance_year': '1234', 'encrypted_student_no_id': '1234QWERASDFZXCV5687TYIUGHKJBNML', 'average_marks': Decimal('56.500'), 'progress_outcome_type_id': 'PCD', 'award_grade': 'R'}
        )

        self.assertEqual(
            retrieve(ProgramInfo, pk="AB004"),
            {'program_code': 'AB004', 'program_title': 'Bachelor of Arts'}
        )

        self.assertEqual(
            retrieve(StudentPrograms, calendar_instance_year='2016', program_code="AB001", encrypted_student_no="00B197BA7753B1F2CFD57570245D62E7"),
            {'calendar_instance_year': '1234', 'program_code_id': 'AB004', 'encrypted_student_no_id': '1234QWERASDFZXCV5687TYIUGHKJBNML', 'degree_complete': False}
        )

        # asserts for third file
        self.assertEqual(
            retrieve(StudentPrograms, calendar_instance_year='2013', program_code="AB000", encrypted_student_no="00B197BA7753B1F2CFD57570245D62E7"),
            {'calendar_instance_year': '2013', 'program_code_id': 'AB000', 'encrypted_student_no_id': '00B197BA7753B1F2CFD57570245D62E7', 'degree_complete': False}
        )

        self.assertEqual(
            retrieve(StudentPrograms, calendar_instance_year='2016', program_code="AB001", encrypted_student_no="00B197BA7753B1F2CFD57570245D62E7"),
            {'calendar_instance_year': '2016', 'program_code_id': 'AB001', 'encrypted_student_no_id': '00B197BA7753B1F2CFD57570245D62E7', 'degree_complete': True}
        )

        self.assertEqual(
            retrieve(StudentInfo, pk="00B197BA7753B1F2CFD57570245D62E3"),
            {'encrypted_student_no': '00B197BA7753B1F2CFD57570245D62E3', 'nationality_short_name': 'South Africa', 'home_language_description': 'Zulu', 'race_description': 'Black', 'gender': 'M', 'age': 45, 'secondary_school_quintile': None, 'urban_rural_secondary_school': None, 'secondary_school_name': 'qwe'}
        )

        self.assertEqual(
            retrieve(ProgressDescription, progress_outcome_type="Q"),
            {'progress_outcome_type': 'Q', 'progress_outcome_type_description': 'Completed all requirements for qualification'}
        )

        self.assertEqual(
            retrieve(StudentPrograms, calendar_instance_year='2017', program_code=None, encrypted_student_no="00B197BA7753B1F2CFD57570245D62E5"),
            {'calendar_instance_year': '2017', 'program_code_id': None, 'encrypted_student_no_id': '00B197BA7753B1F2CFD57570245D62E5', 'degree_complete': False}
        )

        self.assertEqual(
            retrieve(StudentPrograms, calendar_instance_year='2017', program_code="AB001", encrypted_student_no="00B197BA7753B1F2CFD57570245D62E4"),
            {'calendar_instance_year': '2017', 'program_code_id': 'AB001','encrypted_student_no_id': '00B197BA7753B1F2CFD57570245D62E4', 'degree_complete': False}
        )

        self.assertEqual(
            retrieve(YearOfStudy, calendar_instance_year="2016", encrypted_student_no="00B197BA7753B1F2CFD57570245D62E3"),
            {'calendar_instance_year': '2016', 'encrypted_student_no_id': '00B197BA7753B1F2CFD57570245D62E3', 'year_of_study': 'YOS 3'}
        )

        # schools file
        self.assertEqual(
            retrieve(CourseInfo, course_code="AFRL1004"),
            {'course_code': 'AFRL1004', 'course_name': 'AFRL1004', 'school_id': 'Literature, Language and Media'}
        )

        self.assertEqual(
            retrieve(SchoolInfo, school="Literature, Language and Media"),
            {'school': 'Literature, Language and Media', 'faculty': 'Humanities'}
        )

        self.assertEqual(
            retrieve(CourseStats, encrypted_student_no="00B197BA7753B1F2CFD57570245D6210", course_code="INTR1011", calendar_instance_year="2017"),
            {'course_code_id': 'INTR1011', 'calendar_instance_year': '2017', 'encrypted_student_no_id': '00B197BA7753B1F2CFD57570245D6210', 'final_mark': Decimal('61.000'), 'final_grade': 'PAS'}
        )
