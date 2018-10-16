from django.core.management.base import BaseCommand
import os
import logging
from dashboard.apps.dashboard_api.management.util.data_util import load_table
from dashboard.apps.dashboard_api.management.util.inserter import Inserter

logger = logging.getLogger('debug-import')


class DataImportCommand(BaseCommand):
    help = 'help should be overridden'
    options = None

    # set class variable 'header_row' to change import options

    def add_arguments(self, parser):
        if not type(self.options) == dict:
            raise Exception("DataImportCommand must have options defined")
        for name in self.options:
            parser.add_argument(f'--{name}', dest=f'{name}', nargs='*', help='Specify files to be imported')

    def handle(self, *args, **kwargs):
        if not type(self.options) == dict:
            raise Exception("DataImportCommand must have options defined")
        # for each custom option
        for option, import_options in self.options.items():
            # count number of records imported
            imported = 0
            # skip
            if kwargs[option] is None:
                continue
            print(f"\n{'=' * 100}\n")
            # check contents
            assert 'header_row' in import_options
            assert 'models' in import_options
            logger.info(f"[{option}] Importing '{option}' models: {[model.__name__ for model in import_options['models']]}")
            if 'depends_on' in import_options:
                logger.warning(f"[{option}] This stage depends on {import_options['depends_on']}, make sure to import it first.")
            # for each file per custom option
            for file in kwargs[option]:
                if os.path.isfile(file):
                    logger.info(f"[{option}] Importing: {file}")
                else:
                    logger.error(f"[{option}] Cannot find: {file}")
                    exit(1)
                # read table
                df = load_table(file, header=import_options['header_row'], dataframe=True)
                logger.info(f'[{option}] Importing file with columns: {sorted(df.columns)}')
                # rename columns
                df = df.rename(columns=import_options['header_to_field'] if 'header_to_field' in import_options else {})
                # import table
                logger.info(f"[{option}] Importing file with {len(df)} records")
                for i, model in enumerate(import_options['models']):
                    if i > 0:
                        print(f"\n{'- '*50}\n")
                    imported += Inserter(model).insert(df)
            # print results
            logger.info(f"[{option}] Imported: {imported} records from {len(kwargs[option])} files")

            print(f"\n{'='*100}\n")



