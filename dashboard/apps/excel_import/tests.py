from django.test import TestCase
from django.core.management import call_command
from dashboard.apps.excel_import.management.commands.excel_import  import Command
from dashboard.apps.dashboard_api.models import *

from decimal import Decimal

class ExcelImportTestCase(TestCase):
	def setUp(self):
		pass

	# test excel_import custom command with provided files
	def test_specific_excel(self):
		args = ['--file=test_db1.xlsx', '--test']
		opts = {}
		call_command('excel_import', *args, **opts)
		self.assertEqual(\
			StudentInfo.objects.filter(pk="0008F0850D5A573D93162E7F14E46BD1").values().first(),\
			{'encrypted_student_no': '0008F0850D5A573D93162E7F14E46BD1', 'nationality_short_name': 'South Africa', 'home_language_description': 'Setswana', 'race_description': 'Black', 'gender': 'X', 'age': 29, 'secondary_school_quintile': '3', 'urban_rural_secondary_school': 'URBAN', 'secondary_school_name': 'Phahama Senior School'})
		self.assertEqual(\
			CourseStats.objects.filter(encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1").values().first(),\
			{'id': 1, 'course_code': 'ENGL1001', 'calendar_instance_year': '2014', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'year_of_study': 'YOS 1', 'final_mark': Decimal('55.000'), 'final_grade': 'PAS', 'progress_outcome_type': 'PCD', 'award_grade': 'R'})
		self.assertEqual(\
			AverageYearMarks.objects.filter(encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1").values().first(),\
			{'id': 1, 'calendar_instance_year': '2014', 'year_of_study': 'YOS 1', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'average_marks': Decimal('56.500')})
		self.assertEqual(\
			ProgramInfo.objects.filter(pk="AB000").values().first(),\
			{'program_code': 'AB000', 'program_title': 'Bachelor of Arts'})
		self.assertEqual(\
			StudentPrograms.objects.filter(program_code="AB000" , encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1" ).values().first(),\
			{'id': 1, 'program_code_id': 'AB000', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'start_calendar_year': '2014', 'end_calendar_year': '2014'})

	
	# test excel_import custom command without providing files
	# i.e. test importing all files in files directory
	def test_multiple_excel(self):
		args = ['--file=', '--test']
		opts = {}
		call_command('excel_import', *args, **opts)
		# asserts for first file
		self.assertEqual(\
			StudentInfo.objects.filter(pk="0008F0850D5A573D93162E7F14E46BD1").values()[0],\
			{'encrypted_student_no': '0008F0850D5A573D93162E7F14E46BD1', 'nationality_short_name': 'South Africa', 'home_language_description': 'Setswana', 'race_description': 'Black', 'gender': 'X', 'age': 29, 'secondary_school_quintile': '3', 'urban_rural_secondary_school': 'URBAN', 'secondary_school_name': 'Phahama Senior School'})
		temp_dict = CourseStats.objects.filter(encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1").values().first()
		del temp_dict['id']
		self.assertEqual(\
		temp_dict,\
			{'course_code': 'ENGL1001', 'calendar_instance_year': '2014', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'year_of_study': 'YOS 1', 'final_mark': Decimal('55.000'), 'final_grade': 'PAS', 'progress_outcome_type': 'PCD', 'award_grade': 'R'})
		temp_dict = AverageYearMarks.objects.filter(encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1").values()[0]
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'calendar_instance_year': '2014', 'year_of_study': 'YOS 1', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'average_marks': Decimal('56.500')})
		self.assertEqual(\
			ProgramInfo.objects.filter(pk="AB000").values().first(),\
			{'program_code': 'AB000', 'program_title': 'Bachelor of Arts'})
		temp_dict = StudentPrograms.objects.filter(program_code="AB000" , encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1" ).values().first()
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'program_code_id': 'AB000', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'start_calendar_year': '2014', 'end_calendar_year': '2014'})

		# asserts for second file
		self.assertEqual(\
			StudentInfo.objects.filter(pk="1234QWERASDFZXCV5687TYIUGHKJBNML").values().first(),\
				{'encrypted_student_no': '1234QWERASDFZXCV5687TYIUGHKJBNML', 'nationality_short_name': 'South Africa', 'home_language_description': 'Setswana', 'race_description': 'Black', 'gender': 'G', 'age': 29, 'secondary_school_quintile': '3', 'urban_rural_secondary_school': 'URBAN', 'secondary_school_name': 'Phahama Senior School'})
		temp_dict = CourseStats.objects.filter(encrypted_student_no="1234QWERASDFZXCV5687TYIUGHKJBNML").values().first()
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'course_code': 'ENGL1001', 'calendar_instance_year': '1234', 'encrypted_student_no_id': '1234QWERASDFZXCV5687TYIUGHKJBNML', 'year_of_study': 'YOS 1', 'final_mark': Decimal('55.000'), 'final_grade': 'PAS', 'progress_outcome_type': 'PCD', 'award_grade': 'R'})
		temp_dict = AverageYearMarks.objects.filter(encrypted_student_no="1234QWERASDFZXCV5687TYIUGHKJBNML").values()[0]
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'calendar_instance_year': '1234', 'year_of_study': 'YOS 1', 'encrypted_student_no_id': '1234QWERASDFZXCV5687TYIUGHKJBNML', 'average_marks': Decimal('56.500')})
		self.assertEqual(\
			ProgramInfo.objects.filter(pk="AB004").values()[0],\
			{'program_code': 'AB004', 'program_title': 'Bachelor of Arts'})
		temp_dict = StudentPrograms.objects.filter(program_code="AB004" , encrypted_student_no="1234QWERASDFZXCV5687TYIUGHKJBNML" ).values().first()
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'program_code_id': 'AB004', 'encrypted_student_no_id': '1234QWERASDFZXCV5687TYIUGHKJBNML', 'start_calendar_year': '1234', 'end_calendar_year': '1234'})

		# asserts for third file
		temp_dict = StudentPrograms.objects.filter(program_code="AB000" , encrypted_student_no="00B197BA7753B1F2CFD57570245D62E7" ).values().first()
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'program_code_id': 'AB000', 'encrypted_student_no_id': '00B197BA7753B1F2CFD57570245D62E7', 'start_calendar_year': '2013', 'end_calendar_year': '2013'})

		temp_dict = StudentPrograms.objects.filter(program_code="AB001" , encrypted_student_no="00B197BA7753B1F2CFD57570245D62E7" ).values().first()
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'program_code_id': 'AB001', 'encrypted_student_no_id': '00B197BA7753B1F2CFD57570245D62E7', 'start_calendar_year': '2016', 'end_calendar_year': '2016'})
		self.assertEqual(\
			StudentInfo.objects.filter(pk="00B197BA7753B1F2CFD57570245D62E3").values().first(),\
				{'encrypted_student_no': '00B197BA7753B1F2CFD57570245D62E3', 'nationality_short_name': 'South Africa', 'home_language_description': 'Zulu', 'race_description': 'Black', 'gender': 'M', 'age': 45, 'secondary_school_quintile': None, 'urban_rural_secondary_school': None, 'secondary_school_name': 'qwe'})
