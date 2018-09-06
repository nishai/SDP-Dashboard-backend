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

        for path in file_urls:
            self.load_file(path)

    def load_file(self, path):
        df = pd.read_excel(path, index_col=None, header=5)
        df = df.filter(regex='^(?!Unnamed:).*', axis=1)
        df = df.rename(lambda s: s.lower().replace(" ", "_").replace("_/_", "_"), axis='columns')
        items = df.to_dict('records')

        transaction.set_autocommit(False)
        for i, item in enumerate(items):
            try:
                entry = RawStudentModel(**item)
                entry.save()
                if i % 1000 == 0:
                    transaction.commit()
                    print(f"Saved: {i} of {len(items)}")
            except Exception as e:
                print(e)
