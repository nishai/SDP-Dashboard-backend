import pandas as pd

from dashboard.apps.dashboard_api.management.inserter import Inserter
from dashboard.apps.dashboard_api.models import *
from dashboard.apps.dashboard_api.management.data_util import load_table
from django.core.management.base import BaseCommand
import logging
import os

logger = logging.getLogger('debug-import')


class Command(BaseCommand):
    help = 'Imports stats from Wits excel stat files into the database in a normalised form'

    def add_arguments(self, parser):
        parser.add_argument('--files', dest='files', nargs='+', help='Specify file to be important')

    def handle(self, *args, **options):
        imported = 0
        for file in options['files']:
            logger.info(f"Importing: {file}")
            if not os.path.isfile(file):
                logger.error(f"Cannot find: {file}")
                exit(1)
            df = load_table(file, dataframe=True)
            imported += self.import_table(df)
        logger.info(f"Imported: {imported} records from {len(options['files'])} files")

    @staticmethod
    def import_table(df: pd.DataFrame):

        logger.warning("SchoolInfo needs to be imported separately first.")

        models = [
            # SchoolInfo,  # TODO: where do we obtain this data?
            CourseInfo,
            ProgramInfo,
            StudentInfo,
            CourseStats,
            ProgressDescription,
            AverageYearMarks,  # TODO: fix failure on more than one import due to the unique constraint
            YearOfStudy,
            StudentPrograms,
        ]

        logger.info(f"Importing into {len(models)} tables:")

        return sum(Inserter(model).insert(df) for model in models)










