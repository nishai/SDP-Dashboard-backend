import sys
import time
from pprint import pprint
from typing import Dict, List

from django.core.management.base import BaseCommand, CommandError  # for custom manage.py commands
import os  # managing files
import logging
from django.db import transaction
import pandas as pd

# Get an instance of a logger
from django.db.models.fields.related import RelatedField, ForeignKey
from django.db.models.fields.reverse_related import ForeignObjectRel

from dashboard.apps.dashboard_api.models import RawStudentModel, StudentInfo, ProgramInfo, CourseStats, AverageYearMarks

logger = logging.getLogger('debug-import')
logger.debug("Running excel import code")


class Command(BaseCommand):
    help = 'Imports data from excel_import/excel_files/ into the database'

    # inserts the files provided after --files flag into the parser variable for use in handler function
    def add_arguments(self, parser):
        parser.add_argument('--files', dest='files', nargs='+', help='Specify file to be important')
        parser.add_argument('--test', action='store_true', dest='test', help='Specify if this is a test run')
        parser.add_argument('--convert', dest='convert', nargs='*', type=int, help='Convert any excel files to csv and save them')

    def handle(self, *args, **options):
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

        dataframe = None
        for path in file_urls:
            # load file
            df = self.load_file(path)
            # convert xlsx to csv if required
            self.convert_to_csv(df, orig_path=path, **options)
            # import into db
            if options['convert'] is None:
                dataframe = df if dataframe is None else dataframe.append(df)

        if options['convert'] is None:
            logger.info(f"Importing: {len(dataframe)} records")
            self.import_df(dataframe)
            logger.info(f"Imported: {len(dataframe)} records")


    def load_file(self, path):
        ext = os.path.splitext(path)[1].lower()
        logger.info(f"Loading table: {path}")
        if ext == ".xlsx":
            df = pd.read_excel(path, index_col=None, header=5)
        elif ext == ".csv":
            df = pd.read_csv(path, index_col=None)
        else:
            raise Exception(f"Unsupported file extension: {ext}")
        df = df.filter(regex='^(?!Unnamed:).*', axis=1)
        df = df.rename(lambda s: s.lower().replace(" ", "_").replace("_/_", "_"), axis='columns')
        logger.info(f"Table entries loaded: {len(df)}")
        return df

    def convert_to_csv(self, df, orig_path, **options):
        partial, ext = os.path.splitext(orig_path)
        if options['convert'] is not None:
            if len(options['convert']) <= 0:
                options['convert'] += [-1]
            for limit in [l for l in options['convert'] if not (ext.lower() == '.csv' and l < 0)]:
                limit = min(max(-1, limit), len(df))
                path = f"{partial}_{limit}.csv" if limit >= 0 else f"{partial}.csv"
                logger.info(f"Converting to csv: {orig_path} -> {path}")
                df[:limit].to_csv(path, header=True, index=False)

    # def import_df(self, df):
    #     logger.info(f"Converting table to records")
    #     items = df.to_dict('records')
    #     items = [RawStudentModel(**item) for item in items]
    #     logger.info(f"Saving records")
    #     RawStudentModel.objects.bulk_create(items)

# """
#     # Table for program (i.e BSc General) info
#     class ProgramInfo(models.Model):
# !       program_code = models.CharField(max_length=5, primary_key=True)
#         program_title = models.CharField(max_length=255, null=True)
#
#         class Meta:
#             verbose_name = "Program information (i.e information about BSc General Program)"
#
#     # Table for student personal information
#     # Foreign key to program_code in ProgramInfo
#     class StudentInfo(models.Model):
# !       encrypted_student_no = models.CharField(max_length=40, primary_key=True)
#         nationality_short_name = models.CharField(max_length=255, null=True)
#         home_language_description = models.CharField(max_length=30, null=True)
#         race_description = models.CharField(max_length=30, null=True)
#         gender = models.CharField(max_length=1, null=True)
#         age = models.IntegerField(null=True)
#         secondary_school_quintile = models.CharField(max_length=5, null=True)
#         urban_rural_secondary_school = models.CharField(max_length=10, null=True)
#         secondary_school_name = models.CharField(max_length=255, null=True)
# #        program_code = models.ForeignKey('ProgramInfo', on_delete=models.PROTECT)
#
#         class Meta:
#             verbose_name = "Student personal information"
#
#     # Stats of a student in a certain course in a certain year
#     # Foreign keys to student_number in StudentInfo
#     class CourseStats(models.Model):
#         course_code = models.CharField(max_length=8)
#         calendar_instance_year = models.CharField(max_length=4, null=True)
# #        encrypted_student_no = models.ForeignKey('StudentInfo', on_delete=models.CASCADE)
#         year_of_study = models.CharField(max_length=5, null=True)  # Refers to YOS student is registered for
#         # within this course year
#         final_mark = models.DecimalField(max_digits=6, decimal_places=3, null=True)
#         final_grade = models.CharField(max_length=5, null=True)
#         progress_outcome_type = models.CharField(max_length=10, null=True)
#         award_grade = models.CharField(max_length=2, null=True)
#
#         class Meta:
#             verbose_name = "Information about a student for a course in a specific calendar year"
#
#     # Average mark for a student in a specific calendar year
#     class AverageYearMarks(models.Model):
#         calendar_instance_year = models.CharField(max_length=4, null=True)
#         year_of_study = models.CharField(max_length=5, null=True)  # Refers to YOS student is registered for
#         # within this course year
# #        encrypted_student_no = models.ForeignKey('StudentInfo', on_delete=models.CASCADE)
#         average_marks = models.DecimalField(max_digits=6, decimal_places=3, null=True)
#
#         class Meta:
#             verbose_name = "Average mark for a student in a specific calendar year"
# """

    def import_df(self, df: pd.DataFrame):

        logger.info("Importing")

        def get_pk_fields(model_class) -> Dict[str, str]:
            pk = model_class._meta.pk
            if pk.name != 'id':
                pk = [pk]
            else:
                condition = lambda f: f.name != 'id' and not isinstance(f, ForeignObjectRel)  # and not isinstance(f, RelatedField)
                pk = [f for f in model_class._meta.get_fields() if condition(f)]
            pk = {f.name: f for f in pk}
            print(f"[{model_class.__name__}]: PK={list(pk.keys())}")
            return pk

        program_info_pk       = get_pk_fields(ProgramInfo)
        student_info_pk       = get_pk_fields(StudentInfo)
        course_stats_pk       = get_pk_fields(CourseStats)
        average_year_marks_pk = get_pk_fields(AverageYearMarks)

        def get_fields(model_class) -> Dict:
            fields = model_class._meta.get_fields()
            condition = lambda f: f.name != 'id' and not isinstance(f, ForeignObjectRel)  # and not isinstance(f, RelatedField)
            fields = {f.name: f for f in fields if condition(f)}
            print(f"[{model_class.__name__}]: FIELDS={list(fields.keys())}")
            return fields

        program_info_fields       = get_fields(ProgramInfo)
        student_info_fields       = get_fields(StudentInfo)
        course_stats_fields       = get_fields(CourseStats)
        average_year_marks_fields = get_fields(AverageYearMarks)

        def get_fields_foreign(model_class) -> Dict[str, ForeignKey]:
            fields = model_class._meta.get_fields()
            fields = {f.name: f for f in fields if isinstance(f, ForeignKey)}
            print(f"[{model_class.__name__}]: FOREIGN={list(fields.keys())}")
            return fields

        program_info_foreign       = get_fields_foreign(ProgramInfo)
        student_info_foreign       = get_fields_foreign(StudentInfo)
        course_stats_foreign       = get_fields_foreign(CourseStats)
        average_year_marks_foreign = get_fields_foreign(AverageYearMarks)

        def group(model_class, df: pd.DataFrame, pk: Dict, fields: Dict) -> List[Dict]:
            logger.info(f"[{model_class.__name__}]: Grouping...")
            grouped = df.groupby(list(pk.keys()))
            entries = []
            for i, (key, dfgroup) in enumerate(grouped):
                if i % 1000 == 0:
                    print(f"[{model_class.__name__}]: {i} of {len(grouped)}")
                row = dfgroup.iloc[0]       # get first row
                row = row.loc[fields]       # get needed fields from from
                entries += [row.to_dict()]    # convert to dict
            logger.info(f"[{model_class.__name__}]: {len(entries)} {list(pk.keys())}")
            return entries

        programs = group(ProgramInfo, df, program_info_pk, program_info_fields)
        students = group(StudentInfo, df, student_info_pk, student_info_fields)
        stats = group(CourseStats, df, course_stats_pk, course_stats_fields)
        marks = group(AverageYearMarks, df, average_year_marks_pk, average_year_marks_fields)

        @transaction.atomic
        def save(model_class, grouped: List[Dict], foreign: Dict[str, ForeignKey]):
            logger.info(f"[{model_class.__name__}]: loading Foreign Data {len(foreign)}")
            fk_objects = {}
            for fk, fk_field in foreign.items():
                items = {item[fk] for item in grouped}
                fk_objects[fk] = fk_field.foreign_related_fields[0].model.objects.in_bulk(list(items))
            
            pprint(fk_objects)

            logger.info(f"[{model_class.__name__}]: Replacing Foreign Data {len(grouped)}")
            items = [model_class(**{k: fk_objects[k][v] if k in fk_objects else v for k, v in item.items()}) for item in grouped]
            items = {item.pk: item for item in items}

            logger.info(f"[{model_class.__name__}]: Removing duplicates")
            stored = model_class.objects.in_bulk(items.keys())
            insert = {k: v for k, v in items.items() if k not in stored}
            update = {k: v for k, v in items.items() if k in stored}
            logger.info(f"[{model_class.__name__}]: Saving records {len(insert)}")
            model_class.objects.bulk_create(insert.values())

        save(ProgramInfo, programs, program_info_foreign)
        save(StudentInfo, students, student_info_foreign)
        save(CourseStats, stats, course_stats_foreign)
        save(AverageYearMarks, marks, average_year_marks_foreign)




        # logger.info("-----------------------------------------------------------------------")
        # logger.info("Inserting data from table to  models: ")
        # logger.info("-----------------------------------------------------------------------")
        #
        # sys.stdout.flush()
        # try:
        #     api_app = apps.get_app_config('dashboard_api')
        #     api_models = api_app.models.values()
        #
        #     pprint(api_app)
        #     pprint(api_models)
        # except:
        #     pass
        #
        #     for _model in api_models:
        #         logger.info("-----------------------------------------------------------------------")
        #         logger.info("Inserting data to model: " + _model.__name__)
        #         logger.info("-----------------------------------------------------------------------")
        #         sys.stdout.flush()
        #         _model_field_names = [f.name for f in _model._meta.get_fields()]
        #         logger.debug("model fields: " + str(_model_field_names))
        #         logger.debug("titles of excel table" + str(titles))
        #         sys.stdout.flush()
        #
        #         # check for foreign keys
        #         _model_field_objects = [f for f in _model._meta.get_fields()]
        #         foreign_key_fields_dict = {}
        #         for field in _model_field_objects:
        #             if field.__class__ is ForeignKey:
        #                 foreign_key_fields_dict[field.name] = field.related_model
        #         logger.debug("Foreign key fields are: " + str(foreign_key_fields_dict))
        #         sys.stdout.flush()
        #
        #         for row in data:
        #             _model_dict = {key: value for key, value in zip(titles, row) if key in _model_field_names}
        #             # adjust foreign key to their class
        #             for key in _model_dict:
        #                 if key in foreign_key_fields_dict:
        #                     _model_dict[key] = foreign_key_fields_dict[key].objects.get(pk=_model_dict[key])
        #
        #             try:
        #                 # insert to table
        #                 _model.objects.update_or_create(**_model_dict)
        #             except Exception as e:
        #                 logger.warning("error inserting to table, ignored and continued. error is: " + str(e))
        #                 pass
        #         logger.debug("model values: " + str(_model.objects.values()))
        #         sys.stdout.flush()
        #     return 0
        # except Exception as e:
        #     raise Exception("Error inserting data to database with error: " + str(e))
