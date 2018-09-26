# Structure for how to make a custome manage.py command (to run directly without views) from:
# https://docs.djangoproject.com/en/2.1/howto/custom-management-commands/

# usage python3.6 manage.py excel_import [--file <file_name>]

# lines with "pragma: no cover" comments are intended to not be included in code coverage. these lines are safty measures, mostly to help debug, but if the code works as it should these lines should never run, ni matter the input.

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
import logging
# Get an instance of a logger
logger = logging.getLogger('debug-import')
logger.debug("Running excel import code")


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
		logger.info("-----------------------------------------------------------------------")
		logger.info("importing files: " + str(options['files']))
		logger.info("-----------------------------------------------------------------------")
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
		file_urls.sort()
		if os.path.join(mypath,"README.md") in file_urls:
			file_urls.remove(os.path.join(mypath,"README.md"))

		# load data from files file by file
		file_failure = False
		for url in file_urls:
			try:
				# load file data
				all_titles, all_data = self.load_file(url)
			except Exception as e:
				file_failure = True
				logger.error("Error loading file: " + str(e))
				continue

			try:
				# insert data to database worksheet by worksheet
				for i, (sheet_titles, sheet_data) in enumerate(zip(all_titles, all_data)):
					logger.info("-----------------------------------------------------------------------")
					logger.info("adding data for sheet number: " + str(i))
					logger.info("-----------------------------------------------------------------------")
					self.add_data_to_tables(sheet_titles, sheet_data)
			except Exception as e:
				file_failure = True
				logger.error("Error adding data to tables from file " + url + ": " + str(e))

		if file_failure:
			logger.info("Some files had problems importing data to database - see logs")
			return "-1"
		else:
			logger.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
			logger.info("All files imported successfully")
			logger.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
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
		logger.info("-----------------------------------------------------------------------")
		logger.info("Inserting data from table to  models: ")
		logger.info("-----------------------------------------------------------------------")
		try:
			api_app = apps.get_app_config('dashboard_api')
			api_models = api_app.models.values()

			for _model in api_models:
				logger.info("-----------------------------------------------------------------------")
				logger.info("Inserting data to model: " + _model.__name__)
				logger.info("-----------------------------------------------------------------------")
				_model_field_names = [f.name for f in _model._meta.get_fields()]
				logger.debug("model fields: " + str(_model_field_names))
				logger.debug("titles of excel table" + str(titles))

				# check for foreign keys
				_model_field_objects = [f for f in _model._meta.get_fields()]
				foreign_key_fields_dict = {}
				for field in _model_field_objects:
					if field.__class__ is ForeignKey:
						foreign_key_fields_dict[field.name] =  field.related_model
				logger.debug("Foreign key fields are: " + str(foreign_key_fields_dict))

				# check for unique keys
				unique_keys_fields_arr = []
				for field in _model_field_objects:
					if field.__class__ is CharField and (field._unique == True or field.primary_key == True):
						unique_keys_fields_arr.append(field.name)
				if len(_model._meta.unique_together) > 0:
					for field in _model._meta.unique_together[0]:
						unique_keys_fields_arr.append(field)
				logger.debug("Unique keys fields are: " + str(unique_keys_fields_arr))
				
				for row in data:
					_model_dict = {key: value for key, value in zip(titles, row) if key in _model_field_names}
					# check if the entire dictionary has values of None - if so skip this data row
					# foreign key fields don't count, as this model might be empty but the foreign key model might not
					allNone = True
					for key in _model_dict:
						if key != None and not(key in foreign_key_fields_dict):
							allNone = False
					if allNone:
						continue
					# adjust foreign key to their class
					for key in _model_dict:
						if key in foreign_key_fields_dict:
							try:
								_model_dict[key] = foreign_key_fields_dict[key].objects.get(pk=_model_dict[key])
							except:
								logger.warning("foreign key not found for key: " + str(key) + " with value: " + str(_model_dict[key]))
								logger.warning("the _model_dict is: " + str(_model_dict))
								_model_dict[key] = None

					# identify last years of degrees
					if _model.__name__ == "StudentPrograms":
						if row[titles.index("year_of_study")] == "YOS 3" and\
							 row[titles.index("progress_outcome_type")] == "Q":

							_model_dict["degree_complete"] = True
						else:
							_model_dict["degree_complete"] = False
					
					# if a student took a course twice in the same year take the highest mark of the two
					if _model.__name__ == "CourseStats":
						stats_row = CourseStats.objects.filter(\
										encrypted_student_no=_model_dict["encrypted_student_no"],\
										course_code=_model_dict["course_code"],\
										calendar_instance_year=_model_dict["calendar_instance_year"])\
									.values().first()
						if stats_row != None:
							if _model_dict["final_mark"] == None:
								_model_dict["final_mark"] = stats_row["final_mark"]
							elif stats_row["final_mark"] > _model_dict["final_mark"]:
								_model_dict["final_mark"] = stats_row["final_mark"]
								_model_dict["final_grade"] = stats_row["final_grade"]
					try:
						if _model_dict != {}:
							# insert to table
							#logger.debug("inserting dictionary into table: " + str(_model_dict))
							if len(unique_keys_fields_arr) == 0:
								_model.objects.update_or_create(**_model_dict)
							else:
								# if unique keys combination exists in table - update it, otherwise add the row
								unique_keys_dict = {}
								for key in unique_keys_fields_arr:
									unique_keys_dict[key] = _model_dict[key]
								_model.objects.update_or_create(**unique_keys_dict, defaults=_model_dict)
					except Exception as e:
						logger.warning("error inserting to table, ignored and continued. error is: " + str(e))
						logger.warning("row failed to input: " + str(_model_dict))
						pass
				logger.debug("model values: " + str(_model.objects.values()))
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
		logger.info("----------------------------------------------------------------------------")
		logger.info("Attempting to load excel file:\n" + excel_url)
		logger.info("----------------------------------------------------------------------------")
		try:
			with xlrd.open_workbook(excel_url) as workbook:
				worksheet_names = workbook.sheet_names()
				worksheets = []
				for name in worksheet_names:
					logger.info("Loading worksheet: " + name)
					worksheets.append(workbook.sheet_by_name(name))

				all_titles = []
				all_data_lists = []
				for worksheet, name in zip(worksheets, worksheet_names):
					logger.info("extracting data from worksheet: " + name)
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
			if len(file_url) > 4 and file_url[-4:] == ".csv":
				# NOT IMPLEMENTED
				pass
			elif (len(file_url) > 4 and file_url[-4:] == ".xls") or (len(file_url) > 5 and file_url[-5:] == ".xlsx"):
				logger.info("----------------------------------------------------------------------------")
				logger.info(file_url + " Has correct file format for excel files")
				logger.info("----------------------------------------------------------------------------")
				all_titles, all_data = self.load_excel(file_url)
				logger.info("----------------------------------------------------------------------------")
				logger.info("Loading succesful of excel file:\n" + file_url)
				logger.info("----------------------------------------------------------------------------")

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


