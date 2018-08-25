from django.test import TestCase
from excel_import.management.commands  import Command
from dashboard.apps.dashboard_api.models import *

class ExcelImportTestCase(TestCase):
	command = Command.Command()
	def setUp(self):
		pass

	def test_load_excel():
		self.assertEqual(command.load_excel("test_db.xlsx"),\
			([['Encrypted Student No', '', '', 'Calendar Instance Year', 'Program Code', 'Program Title', '', 'Year of Study', 'Nationality Short Name', '', '', 'Home Language Description', 'Race Description', 'Gender', 'Age', 'Course Code', 'Final Mark', 'Final Grade', 'Progress Outcome Type', 'Progress Outcome Type Description', 'Award Grade', 'Average Marks', 'Secondary School Quintile', 'Urban Rural Secondary School', 'Secondary School Name'],\
			['QWE', 'ASD', 'ZXC']],\
			[[['0008F0850D5A573D93162E7F14E46BD1','','',	'2014',	'AB000','Bachelor of Arts','',	'YOS 1', 'South Africa','','',	'Setswana',	'Black', 'M', '29',	'ENGL1001', '55', 'PAS', 'PCD',	'Permitted to proceed',	'R','56.5',	'3',	'URBAN', 'Phahama Senior School'],\
				['0008F0850D5A573D93162E7F14E46BD1',	'',	'',	'2014',	'AB001', 'Bachelor of Arts', '', 'YOS 1', 'South Africa', '', '', 'Setswana', 'Black', 'X', '29', 'ENGL1001', '44',	'PAS',	'PCD',	'Permitted to proceed',	None, '56.5', '3', 'URBAN', 'Phahama Senior School'],\
				['004A51D4390D5B4DF6B1DE331512BB7B', '', '', '2017', 'AB000', 'Bachelor of Arts', '', 'YOS 2', 'South Africa', '', '', 'Zulu', 'Black', 'M', '26', 'ENGL2003', '37', 'FAL', 'PCD', 'Permitted to proceed', 'U',	'58.17', None, 'UN']],\
			[['rty','fgh','vbn']]]))

	def test_load_file():
		self.assertEqual(command.load_file("test_db.xlsx"),\
			([['encrypted_student_no', '', '', 'calendar_instance_year', 'program_code', 'program_title', '', 'year_of_study', 'nationality_short_name', '', '', 'home_language_description', 'race_description', 'gender', 'age', 'course_code', 'final_mark', 'final_grade', 'progress_outcome_type', 'progress_outcome_type_description', 'award_grade', 'average_marks', 'secondary_school_quintile', 'urban_rural_secondary_school', 'secondary_school_name'],\
			['qwe', 'asd', 'zxc']],\
			[[('0008F0850D5A573D93162E7F14E46BD1','','',	'2014',	'AB000','Bachelor of Arts','',	'YOS 1', 'South Africa','','',	'Setswana',	'Black', 'M', '29',	'ENGL1001', '55', 'PAS', 'PCD',	'Permitted to proceed',	'R','56.5',	'3',	'URBAN', 'Phahama Senior School'),\
				('0008F0850D5A573D93162E7F14E46BD1',	'',	'',	'2014',	'AB001', 'Bachelor of Arts', '', 'YOS 1', 'South Africa', '', '', 'Setswana', 'Black', 'X', '29', 'ENGL1001', '44',	'PAS',	'PCD',	'Permitted to proceed',	None, '56.5', '3', 'URBAN', 'Phahama Senior School'),\
				('004A51D4390D5B4DF6B1DE331512BB7B', '', '', '2017', 'AB000', 'Bachelor of Arts', '', 'YOS 2', 'South Africa', '', '', 'Zulu', 'Black', 'M', '26', 'ENGL2003', '37', 'FAL', 'PCD', 'Permitted to proceed', 'U',	'58.17', None, 'UN')],\
			[('rty','fgh','vbn')]]))

	def test_add_data_to_tables():
		self.assertEqual(command.add_data_to_tables(\
			[['encrypted_student_no', '', '', 'calendar_instance_year', 'program_code', 'program_title', '', 'year_of_study', 'nationality_short_name', '', '', 'home_language_description', 'race_description', 'gender', 'age', 'course_code', 'final_mark', 'final_grade', 'progress_outcome_type', 'progress_outcome_type_description', 'award_grade', 'average_marks', 'secondary_school_quintile', 'urban_rural_secondary_school', 'secondary_school_name']],\
			[('0008F0850D5A573D93162E7F14E46BD1','','',    '2014', 'AB000','Bachelor of Arts','',  'YOS 1', 'South     Africa','','',  'Setswana', 'Black', 'M', '29', 'ENGL1001', '55', 'PAS', 'PCD', 'Permitted to proceed', 'R','56.5'    , '3',    'URBAN', 'Phahama Senior School')]
		), 0)
		self.assertEqual(command.add_data_to_tables(['qwe', 'asd', 'zxc'], [('rty','fgh','vbn')], 0))

	def test_specific_excel():
		command.handler(options=['test_db.xlsx'])
		self.assertEqual(StudentInfo.objects.filter(pk="0008F0850D5A573D93162E7F14E46BD1").age, 29)

	def test_all_excel():
		command.handler(options=[])
		pass
