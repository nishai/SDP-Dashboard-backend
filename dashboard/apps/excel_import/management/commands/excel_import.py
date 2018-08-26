# Structure for how to make a custome manage.py command (to run directly without views) from:
# https://docs.djangoproject.com/en/2.1/howto/custom-management-commands/

# usage python3.6 manage.py excel_import [--file <file_name>]


# project imports
from dashboard.apps.dashboard_api.models import *

#django imports
from django.core.management.base import BaseCommand, CommandError # for custom manage.py commands
from django.apps import apps
from django.db.models import *
import django.apps

#system imports
import sys
import xlrd # excel file importing
import os #managing files

# import the logging library
#import logging
# Get an instance of a logger
#logger = logging.getLogger(__name__)

class Command(BaseCommand):
	help = 'Imports data from excel_import/excel_files/ into the database'

	# inserts the files provided after --files flag into the parser variable for use in handler function
	def add_arguments(self, parser):
		parser.add_argument('--files', dest='files', nargs='+', help='Specify file to be important')
		parser.add_argument('--test', action='store_true', dest='test', help='Specify if this is a test run')

	# Description:
	# 	Go through all the excel files provided using the --files flag (if non are provided use all files available)
	# 	Extract the titles of columns and data from each worksheet in each file
	# 	File by file, worksheet by worksheet, insert the data into the existing table models available
	# Input: file names after the --files flag
	# Output: 
	#	success: returns 0. Data will be inserted directly into the model tables.
	#	failure: raises exception
	def handle(self, *args, **options):
		print("-----------------------------------------------------------------------")
		print("importing files: " + str(options['files']))
		print("-----------------------------------------------------------------------")
		# obtain absolute path for excel files directory
		mypath = os.path.join(os.path.abspath(os.path.join(__file__,os.path.join(*[os.pardir]*3))),"excel_files")
		if options['test']:
			mypath = os.path.join(mypath,"test_excels")
		# create a list of all excel files
		if options['files'][0] != '':
			# If file names are provided, use them
			file_urls = [os.path.join(mypath,f) for f in options['files'] if os.path.isfile(os.path.join(mypath, f))]
		else:
			# If no file name is provided take all files in the folder
			file_urls = [os.path.join(mypath,f) for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

		# load data from files file by file
		file_failure = False
		for url in file_urls:
			try:
				# load file data
				all_titles, all_data = self.load_file(url)
			except Exception as e:
				file_failure = True
				print("Error loading file: " + str(e))
				continue

			try:
				# insert data to database worksheet by worksheet
				for sheet_titles, sheet_data in zip(all_titles, all_data):
					self.add_data_to_tables(sheet_titles, sheet_data)
			except Exception as e:
				file_failure = True
				print("Error adding data to tables from file " + url + ": " + str(e))

		if file_failure:
			raise Exception("Some files had problems importing data to database - see warnings")
		else:
			print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
			print("All files imported successfully")
			print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
			return 0

	# Description:
	#	Insert data into the models available as follows:
	# 	Go through all available models
	# 	Extract the titles and data according to the fields availablel in each model
	# 	Insert the data of the fields that the model has into the model, row by row
	# 	NOTICE: This assumes the titles and the model fields names match!
	# Input: titles (column names) of a tabele, data of a table as a list of tuples
	# Output:
	#	success: returns 0. The database will have the data provided inserted into it
	#	failure: raises exception
	def add_data_to_tables(self, titles, data):
		print("-----------------------------------------------------------------------")
		print("Inserting data from table to  models: ")
		print("-----------------------------------------------------------------------")
		sys.stdout.flush()
		try:
			api_app = apps.get_app_config('dashboard_api')
			api_models = api_app.models.values()

			for _model in api_models:
				print("-----------------------------------------------------------------------")
				print("Inserting data to model: " + _model.__name__)
				print("-----------------------------------------------------------------------")
				sys.stdout.flush()
				_model_field_names = [f.name for f in _model._meta.get_fields()]
				print("model fields: " + str(_model_field_names))
				print("titles of excel table" + str(titles))
				sys.stdout.flush()

				# check for foreign keys
				_model_field_objects = [f for f in _model._meta.get_fields()]
				foreign_key_fields_dict = {}
				for field in _model_field_objects:
					if field.__class__ is ForeignKey:
						foreign_key_fields_dict[field.name] =  field.related_model
				print("Foreign key fields are: " + str(foreign_key_fields_dict))
				sys.stdout.flush()

				for row in data:
					_model_dict = {key: value for key, value in zip(titles, row) if key in _model_field_names}
					# adjust foreign key to their class
					for key in _model_dict:
						if key in foreign_key_fields_dict:
							_model_dict[key] = foreign_key_fields_dict[key].objects.get(pk=_model_dict[key])

					try:
						# insert to table
						_model.objects.update_or_create(**_model_dict)
					except Exception as e:
						pass
				print("model values: " + str(_model.objects.values()))
				sys.stdout.flush()
			return 0
		except Exception as e:
			raise Exception("Error inserting data to database with error: " + str(e))

	# https://stackoverflow.com/questions/26029095/python-convert-excel-to-csv#26030521
	# Description:
	#	load data from the excel files, worksheet by worksheet, using the xlrd library
	# Input: url to excel file
	# Output:
	#	success:
	#		returns a list of the titles row (names of collumns)
	#		and a list of the data as a list for each row (list of lists)
	# 	failure: raise an exception
	def load_excel(self, excel_url):
		print("----------------------------------------------------------------------------")
		print("Attempting to load excel file:\n" + excel_url)
		print("----------------------------------------------------------------------------")
		sys.stdout.flush()
		try:
			with xlrd.open_workbook(excel_url) as workbook:
				worksheet_names = workbook.sheet_names()
				worksheets = []
				for name in worksheet_names:
					print("Loading worksheet: " + name)
					worksheets.append(workbook.sheet_by_name(name))

				all_titles = []
				all_data_lists = []
				for worksheet, name in zip(worksheets, worksheet_names):
					print("extracting data from worksheet: " + name)
					titles = worksheet.row_values(0)
					all_titles.append(titles)

					sheet_data_list = []
					for rownum in range(1,worksheet.nrows):
						sheet_data_list += [worksheet.row_values(rownum)]
					all_data_lists.append(sheet_data_list)

				return all_titles, all_data_lists

		except Exception as e:
			raise Exception("failed loading excel file: " + excel_url + " with error: " + str(e))


	# Description:
	#	Determine if given file has a correct file type
	#	If valid file type send the data for loading appropriate file type
	#	and parse the titles to be snake_case and data to be tuples
	#	If file type is not valid raise an exception
	# Input: file url string
	# Output:
	#	success: properly formatted titles and data
	#	fail: raise exception
	def load_file(self, file_url):
		try:
			if file_url[-4:] == ".csv":
				# NOT IMPLEMENTED
				pass
			elif file_url[-4:] == ".xls" or file_url[-5:] == ".xlsx":
				print("----------------------------------------------------------------------------")
				print(file_url + " Has correct file format for excel files")
				print("----------------------------------------------------------------------------")
				sys.stdout.flush()
				all_titles, all_data = self.load_excel(file_url)
				print("----------------------------------------------------------------------------")
				print("Loading succesful of excel file:\n" + file_url)
				print("----------------------------------------------------------------------------")
				sys.stdout.flush()				

				# adapt titles to snake case
				all_titles =\
					 [[col.replace(" ","_").replace("_/_","_").lower() for col in sheet_titles] \
					 for sheet_titles in all_titles]
				# adapt data from lists to tuples		
				all_data = [[[i if i != '' else None for i in row] for row in sheet_data]\
					 for sheet_data in all_data]
				all_data = [[tuple(row) for row in sheet_data]\
					 for sheet_data in all_data]
			else:
				raise Exception("bad file type provided. only .csv, .xls, .xlsx accepted.")
			return all_titles, all_data
		except Exception as e:
			raise Exception("error loading data from file " + file_url + " : " + str(e))


