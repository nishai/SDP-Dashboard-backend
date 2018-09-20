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
		args = ['--file=a_test_schools.xlsx', '--test']
		opts = {}
		self.assertEqual(call_command('excel_import', *args, **opts), 0)
		args = ['--file=b_test_db1.xlsx', '--test']
		opts = {}
		self.assertEqual(call_command('excel_import', *args, **opts), 0)
		self.assertEqual(\
			StudentInfo.objects.filter(pk="0008F0850D5A573D93162E7F14E46BD1").values().first(),\
			{'encrypted_student_no': '0008F0850D5A573D93162E7F14E46BD1', 'nationality_short_name': 'South Africa', 'home_language_description': 'Setswana', 'race_description': 'Black', 'gender': 'X', 'age': 29, 'secondary_school_quintile': '3', 'urban_rural_secondary_school': 'URBAN', 'secondary_school_name': 'Phahama Senior School'})
		self.assertEqual(\
			CourseStats.objects.filter(encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1", course_code="ENGL1001", calendar_instance_year="2014").values().first(),\
			{'id': 1, 'course_code_id': 'ENGL1001', 'calendar_instance_year': '2014', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'final_mark': Decimal('44.000'), 'final_grade': 'PAS'})
		self.assertEqual(\
			AverageYearMarks.objects.filter(encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1", calendar_instance_year="2014").values().first(),\
			{'id': 1, 'calendar_instance_year': '2014', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'average_marks': Decimal('56.500'), 'progress_outcome_type_id': 'PCD', 'award_grade': None})
		self.assertEqual(\
			ProgramInfo.objects.filter(pk="AB000").values().first(),\
			{'program_code': 'AB000', 'program_title': 'Bachelor of Arts'})
		self.assertEqual(\
			StudentPrograms.objects.filter(calendar_instance_year='2014', program_code="AB000" , encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1" ).values().first(),\
			{'id': 1, 'calendar_instance_year': '2014','program_code_id': 'AB000', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'degree_complete': False})
		self.assertEqual(ProgressDescription.objects.filter(progress_outcome_type="PCD").values().first(), {'progress_outcome_type':'PCD' , 'progress_outcome_type_description':'Permitted to proceed'})

	
	# test excel_import custom command without providing files
	# i.e. test importing all files in files directory
	def test_multiple_excel(self):
		args = ['--file=', '--test']
		opts = {}
		self.assertEqual(call_command('excel_import', *args, **opts), "-1")
		# asserts for first file
		self.assertEqual(\
			StudentInfo.objects.filter(pk="0008F0850D5A573D93162E7F14E46BD1").values()[0],\
			{'encrypted_student_no': '0008F0850D5A573D93162E7F14E46BD1', 'nationality_short_name': 'South Africa', 'home_language_description': 'Setswana', 'race_description': 'Black', 'gender': 'X', 'age': 29, 'secondary_school_quintile': '3', 'urban_rural_secondary_school': 'URBAN', 'secondary_school_name': 'Phahama Senior School'})
		temp_dict = CourseStats.objects.filter(encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1", course_code="ENGL1001", calendar_instance_year="2014").values().first()
		del temp_dict['id']
		self.assertEqual(\
		temp_dict,\
			{'course_code_id': 'ENGL1001', 'calendar_instance_year': '2014', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'final_mark': Decimal('44.000'), 'final_grade': 'PAS'})
		temp_dict = AverageYearMarks.objects.filter(encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1", calendar_instance_year="2014").values()[0]
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'calendar_instance_year': '2014', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'average_marks': Decimal('56.500'), 'progress_outcome_type_id': 'PCD', 'award_grade': None})
		self.assertEqual(\
			ProgramInfo.objects.filter(pk="AB000").values().first(),\
			{'program_code': 'AB000', 'program_title': 'Bachelor of Arts'})
		temp_dict = StudentPrograms.objects.filter(calendar_instance_year='2014', program_code="AB000" , encrypted_student_no="0008F0850D5A573D93162E7F14E46BD1" ).values().first()
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'calendar_instance_year': '2014', 'program_code_id': 'AB000', 'encrypted_student_no_id': '0008F0850D5A573D93162E7F14E46BD1', 'degree_complete': False})

		# asserts for second file
		self.assertEqual(\
			StudentInfo.objects.filter(pk="1234QWERASDFZXCV5687TYIUGHKJBNML").values().first(),\
				{'encrypted_student_no': '1234QWERASDFZXCV5687TYIUGHKJBNML', 'nationality_short_name': 'South Africa', 'home_language_description': 'Setswana', 'race_description': 'Black', 'gender': 'G', 'age': 29, 'secondary_school_quintile': '3', 'urban_rural_secondary_school': 'URBAN', 'secondary_school_name': 'Phahama Senior School'})
		temp_dict = CourseStats.objects.filter(encrypted_student_no="1234QWERASDFZXCV5687TYIUGHKJBNML", course_code="ENGL1001", calendar_instance_year="1234").values().first()
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'course_code_id': 'ENGL1001', 'calendar_instance_year': '1234', 'encrypted_student_no_id': '1234QWERASDFZXCV5687TYIUGHKJBNML', 'final_mark': Decimal('55.000'), 'final_grade': 'PAS'})
		temp_dict = AverageYearMarks.objects.filter(encrypted_student_no="1234QWERASDFZXCV5687TYIUGHKJBNML", calendar_instance_year="1234").values()[0]
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'calendar_instance_year': '1234', 'encrypted_student_no_id': '1234QWERASDFZXCV5687TYIUGHKJBNML', 'average_marks': Decimal('56.500'), 'progress_outcome_type_id': 'PCD', 'award_grade': 'R'})
		self.assertEqual(\
			ProgramInfo.objects.filter(pk="AB004").values()[0],\
			{'program_code': 'AB004', 'program_title': 'Bachelor of Arts'})
		temp_dict = StudentPrograms.objects.filter(calendar_instance_year='1234', program_code="AB004" , encrypted_student_no="1234QWERASDFZXCV5687TYIUGHKJBNML" ).values().first()
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'calendar_instance_year': '1234','program_code_id': 'AB004', 'encrypted_student_no_id': '1234QWERASDFZXCV5687TYIUGHKJBNML', 'degree_complete': False})

		# asserts for third file
		temp_dict = StudentPrograms.objects.filter(calendar_instance_year='2013', program_code="AB000" , encrypted_student_no="00B197BA7753B1F2CFD57570245D62E7" ).values().first()
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'calendar_instance_year': '2013','program_code_id': 'AB000', 'encrypted_student_no_id': '00B197BA7753B1F2CFD57570245D62E7', 'degree_complete': False})

		temp_dict = StudentPrograms.objects.filter(calendar_instance_year='2016', program_code="AB001" , encrypted_student_no="00B197BA7753B1F2CFD57570245D62E7" ).values().first()
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'calendar_instance_year': '2016', 'program_code_id': 'AB001', 'encrypted_student_no_id': '00B197BA7753B1F2CFD57570245D62E7', 'degree_complete': True})
		self.assertEqual(\
			StudentInfo.objects.filter(pk="00B197BA7753B1F2CFD57570245D62E3").values().first(),\
				{'encrypted_student_no': '00B197BA7753B1F2CFD57570245D62E3', 'nationality_short_name': 'South Africa', 'home_language_description': 'Zulu', 'race_description': 'Black', 'gender': 'M', 'age': 45, 'secondary_school_quintile': None, 'urban_rural_secondary_school': None, 'secondary_school_name': 'qwe'})
		self.assertEqual(ProgressDescription.objects.filter(progress_outcome_type="Q").values().first(), {'progress_outcome_type':'Q' , 'progress_outcome_type_description':'Completed all requirements for qualification'})
		
		temp_dict = StudentPrograms.objects.filter(calendar_instance_year='2017', program_code=None , encrypted_student_no="00B197BA7753B1F2CFD57570245D62E5" ).values().first()
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'calendar_instance_year': '2017', 'program_code_id': None, 'encrypted_student_no_id': '00B197BA7753B1F2CFD57570245D62E5', 'degree_complete': False})

		temp_dict = StudentPrograms.objects.filter(calendar_instance_year='2017', program_code="AB001" , encrypted_student_no="00B197BA7753B1F2CFD57570245D62E4" ).values().first()
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'calendar_instance_year': '2017', 'program_code_id': 'AB001', 'encrypted_student_no_id': '00B197BA7753B1F2CFD57570245D62E4', 'degree_complete': False})
	
		temp_dict = YearOfStudy.objects.filter(calendar_instance_year="2016" , encrypted_student_no="00B197BA7753B1F2CFD57570245D62E3" ).values().first()
		del temp_dict['id']
		self.assertEqual(\
			temp_dict,\
			{'calendar_instance_year': '2016', 'encrypted_student_no_id': '00B197BA7753B1F2CFD57570245D62E3', 'year_of_study': 'YOS 3'})
		#schools file
		self.assertEqual(CourseInfo.objects.filter(course_code="AFRL1004").values().first(), {'course_code': 'AFRL1004', 'school_id': 'Literature, Language and Media'})
		self.assertEqual(SchoolInfo.objects.filter(school="Literature, Language and Media").values().first(), {'school': 'Literature, Language and Media', 'faculty': 'Humanities'})
