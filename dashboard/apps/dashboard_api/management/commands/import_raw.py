from django.core.management.base import BaseCommand
import os
import logging
from dashboard.apps.dashboard_api.management.data_util import load_table
from dashboard.apps.dashboard_api.models import RawStudentModel

logger = logging.getLogger('debug-import')
logger.debug("Running excel import code")


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
    def import_table(df):
        logger.info(f"Converting table to dict")
        items = df.to_dict('records')
        logger.info(f"Converting table to records")
        items = [RawStudentModel(**item) for item in items]
        logger.info(f"Saving records")
        return len(RawStudentModel.objects.bulk_create(items))
