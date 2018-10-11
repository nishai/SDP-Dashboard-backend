import pandas as pd
from dashboard.apps.dashboard_api.management.inserter import Inserter
from dashboard.apps.dashboard_api.models import StudentInfo, ProgramInfo, CourseStats, AverageYearMarks, RawStudentModel
from dashboard.apps.dashboard_api.management.data_util import load_table
from django.core.management.base import BaseCommand
import logging
import os

logger = logging.getLogger('debug-import')


class Command(BaseCommand):
    help = 'Imports data from excel_import/excel_files/ into the database'

    def add_arguments(self, parser):
        parser.add_argument('--files', dest='files', nargs='+', help='Specify file to be important')

    def handle(self, *args, **options):
        imported = 0
        for file in options['files']:
            logger.info(f"Importing: {file}")
            assert os.path.isfile(file)
            df = load_table(file, dataframe=True)
            imported += self.import_table(df)
        logger.info(f"Imported: {imported} records from {len(options['files'])} files")

    @staticmethod
    def import_table(df: pd.DataFrame):
        models = [
            RawStudentModel,
            ProgramInfo,
            StudentInfo,
            CourseStats,
            AverageYearMarks
        ]

        logger.info(f"Importing into {len(models)} tables:")

        return sum(Inserter(model).insert(df) for model in models)
