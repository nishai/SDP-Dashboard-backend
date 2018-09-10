import sys
import time

from django.core.management.base import BaseCommand, CommandError  # for custom manage.py commands
import os  # managing files
import logging
from django.db import transaction
import pandas as pd

# Get an instance of a logger
from dashboard.apps.dashboard_api.models import RawStudentModel

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

        imported = 0
        for path in file_urls:
            try:
                # load file
                df = self.load_file(path)
                # convert xlsx to csv if required
                self.convert_to_csv(df, orig_path=path, **options)
                # import into db
                if options['convert'] is None:
                    self.import_df(df)
                    imported += len(df)
            except Exception as e:
                logger.error(e)

        if options['convert'] is None:
            logger.info(f"Imported: {imported} records")


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

    def import_df(self, df):
        logger.info(f"Converting table to records")
        items = df.to_dict('records')
        items = [RawStudentModel(**item) for item in items]
        logger.info(f"Saving records")
        RawStudentModel.objects.bulk_create(items)
