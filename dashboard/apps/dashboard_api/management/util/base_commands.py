from django.core.management.base import BaseCommand
import os
import logging
from dashboard.apps.dashboard_api.management.util.data_util import load_table

logger = logging.getLogger('debug-import')


class DataImportCommand(BaseCommand):
    help = 'help should be overridden'

    # set class variable 'header_row' to change import options

    def add_arguments(self, parser):
        parser.add_argument('--files', dest='files', nargs='+', help='Specify file to be important')

    def handle(self, *args, **options):
        imported = 0
        for file in options['files']:
            logger.info(f"Importing: {file}")
            if not os.path.isfile(file):
                logger.error(f"Cannot find: {file}")
                exit(1)
            df = load_table(file, header=self.header_row if hasattr(self, 'header_row') else 0, dataframe=True)
            logger.info(f'File Columns Found - {", ".join(df.columns)}')
            imported += self.import_table(df)
        logger.info(f"Imported: {imported} records from {len(options['files'])} files")

    def import_table(self, df):
        raise NotImplementedError("Override me")
