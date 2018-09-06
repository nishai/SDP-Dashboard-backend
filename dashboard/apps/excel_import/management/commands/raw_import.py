# Structure for how to make a custome manage.py command (to run directly without views) from:
# https://docs.djangoproject.com/en/2.1/howto/custom-management-commands/

# usage python3.6 manage.py excel_import [--file <file_name>]

# django imports
from django.core.management.base import BaseCommand, CommandError  # for custom manage.py commands
from django.apps import apps
from django.db.models import *
# system imports
import sys
import xlrd  # excel file importing
import os  # managing files
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

    def handle(self, *args, **options):
        """
        Description:
            Go through all the excel files provided using the --files flag (if non are provided use all files available)
            Extract the titles of columns and data from each worksheet in each file
            File by file, worksheet by worksheet, insert the data into the existing table models available
        Input: file names after the --files flag
        Output:
           success: returns 0. Data will be inserted directly into the model tables.
           failure: raises exception
               :param args:
               :param options:
               :return:
        """
        logger.info("-----------------------------------------------------------------------")
        logger.info("importing files: " + str(options['files']))
        logger.info("-----------------------------------------------------------------------")

        # obtain absolute path for excel files directory
        mypath = os.path.join(os.path.abspath(os.path.join(__file__, os.path.join(*[os.pardir] * 3))), "excel_files")
        if options['test']:
            mypath = os.path.join(mypath, "test_excels")
        # create a list of all excel files
        if options['files'][0] != '':
            # If file names are provided, use them
            file_urls = [os.path.join(mypath, f) for f in options['files'] if os.path.isfile(os.path.join(mypath, f))]
        else:
            # If no file name is provided take all files in the folder
            file_urls = [os.path.join(mypath, f) for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

        # load data from files file by file
        file_failure = False

        for path in file_urls:
            try:
                # load file data
                all_titles, all_data = self.load_file(path)
            except Exception as e:
                file_failure = True
                logger.error("Error loading file: " + str(e))
                continue

            try:
                # insert data to database worksheet by worksheet
                # for sheet_titles, sheet_data in zip(all_titles, all_data):
                #     self.add_data_to_tables(sheet_titles, sheet_data)
                pass
            except Exception as e:
                file_failure = True
                logger.error("Error adding data to tables from file " + path + ": " + str(e))

        if file_failure:
            raise Exception("Some files had problems importing data to database - see logs")
        else:
            logger.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            logger.info("All files imported successfully")
            logger.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            return 0

    def load_file(self, file_path):
        import pandas as pd
        import messytables as mt
        import time

        start = time.time()
        def xlrd_load():
            try:
                startb = time.time()
                with xlrd.open_workbook(file_path) as workbook:
                    logger.info(f"XLRD A: {time.time() - startb}s")
                    startb = time.time()

                    logger.info(f"{list(workbook)}")

                    worksheet_names = workbook.sheet_names()
                    worksheets = []
                    for name in worksheet_names:
                        logger.info("Loading worksheet: " + name)
                        worksheets.append(workbook.sheet_by_name(name))

                    logger.info(f"XLRD B: {time.time() - startb}s")
                    startb = time.time()

                    all_titles = []
                    all_data_lists = []
                    for worksheet, name in zip(worksheets, worksheet_names):
                        logger.info("extracting data from worksheet: " + name)
                        titles = worksheet.row_values(0)
                        all_titles.append(titles)

                        logger.info(f"TITLES: {all_titles}")

                        sheet_data_list = []
                        for rownum in range(1, worksheet.nrows):
                            sheet_data_list += [worksheet.row_values(rownum)]
                        all_data_lists.append(sheet_data_list)

                    logger.info(f"XLRD C: {time.time() - startb}s {all_titles}")

                    return all_titles, all_data_lists
            except Exception as e:
                raise Exception("failed loading excel file: " + file_path + " with error: " + str(e))
        xlrd_load()
        logger.info(f"XLRD: {time.time() - start}s")

        start = time.time()
        try:
            logger.info(f"LOADING WITH PANDAS")
            df = pd.read_excel(file_path)
            logger.info(f"HEAD 10: \n{df.head(10)}")
            logger.info(f"COLS: {list(df)}")
            logger.info(f"LEN: {len(df)}")

        except Exception as e:
            logger.error(f"Failed to load with messytable: {file_path}")
            return []
        logger.info(f"PANDAS: {time.time() - start}s")

        with open(file_path, 'rb') as file:
            start = time.time()
            try:
                logger.info(f"LOADING WITH MESSYTABLES")
                startb = time.time()
                table = mt.XLSTableSet(file).tables[0]
                offset, headers = mt.headers_guess(table.sample)
                table.register_processor(mt.headers_processor(headers))
                table.register_processor(mt.offset_processor(offset + 1))
                # table.register_processor(mt.types_processor(mt.type_guess(table.sample, strict=True)))
                logger.info(f"LOADING WITH MESSYTABLESL {time.time() - startb}s")
                logger.info(f"IMPORTING WITH MESSYTABLE: {headers}")
                startb = time.time()
                import_data = [{c.column: c.value for c in row} for row in table]
                logger.info(f"IMPORTING WITH MESSYTABLES: {time.time() - startb}s {import_data[0]} {import_data[1]}")
            except Exception as e:
                logger.error(f"Failed to load with messytable: {file_path}")
                return []
            logger.info(f"MESSYTABLES: {time.time() - start}s")

        b = ['', '', 'Encrypted Student No', '', '', 'Calendar Instance Year', 'Program Code', 'Program Title', '',
         'Year of Study', 'Nationality Short Name', '', '', 'Home Language Description', '', 'Race Description',
         'Gender', 'Age', 'Course Code', 'Final Mark', 'Final Grade', 'Progress Outcome Type',
         'Progress Outcome Type Description', 'Award Grade', 'Average Marks', 'Secondary School Quintile',
         'Urban / Rural Secondary School', 'Secondary School Name']

        a = {'column_0': '', 'column_1': '', 'Encrypted Student No': '0021D31BE03E4AB097DCF9C0C89B13BA', 'column_3': '',
         'column_4': '', 'Calendar Instance Year': '2013', 'Program Code': 'SB000',
         'Program Title': 'Bachelor of  Science', 'column_8': '', 'Year of Study': 'YOS 2',
         'Nationality Short Name': 'South Africa', 'column_11': '', 'column_12': '',
         'Home Language Description': 'South Sotho', 'column_14': '', 'Race Description': 'Black', 'Gender': 'F',
         'Age': 25.0, 'Course Code': 'CHEM2003', 'Final Mark': 50.0, 'Final Grade': 'PMP',
         'Progress Outcome Type': 'PCD', 'Progress Outcome Type Description': 'Permitted to proceed', 'Award Grade': '',
         'Average Marks': 60.75, 'Secondary School Quintile': '4', 'Urban / Rural Secondary School': 'URBAN',
         'Secondary School Name': 'Forte Secondary School'}



        # col_rename = {'Calendar Instance Year': 'year', 'Club Society Id': 'club_id',
        #               'Club Society Name': 'club_name', 'Register Flag': 'deregistered',
        #               'Student Number': 'student_num', 'First Name': 'fname', 'Last Name': 'lname',
        #               'Mobile Number': 'phone', 'Primary Email Address': 'email', 'Race Description': 'race'}
        # col_keep = {'fname', 'lname', 'year', 'student_num', 'deregistered', 'phone', 'email'}
        # col_mutate = {
        #     'fname': lambda x: re.sub("[^a-zA-Z ]", "", x).strip().lower(),
        #     'lname': lambda x: re.sub("[^a-zA-Z ]", "", x).strip().lower(),
        #     'deregistered': lambda x: False if (x == "Registered") else True if (x == "De-Registered") else None,
        #     'phone': lambda x: fix_phone_number(x).strip().lower(),
        #     'email': lambda x: x.strip().lower(),
        #     'year': lambda x: int(x.strip().lower()),
        #     'student_num': lambda x: x.strip().lower().split('.')[0]
        # }
        #
        # return mutate_dict_list(import_data, col_renames=col_rename, col_keep=col_keep, col_mutate=col_mutate)
