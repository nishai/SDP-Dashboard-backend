import io
from typing import Union, List
from django.core.management.base import BaseCommand
import os
import logging
import pandas as pd

from dashboard.apps.wits.management.util.datainserter import Inserter

logger = logging.getLogger('debug-import')


class DataImportCommand(BaseCommand):
    help = 'help should be overridden'
    options = None

    # set class variable 'header_row' to change import options

    def add_arguments(self, parser):
        if not type(self.options) == dict: # pragma: no cover
            raise Exception("DataImportCommand must have options defined")
        for name in self.options:
            parser.add_argument(f'--{name}', dest=f'{name}', nargs='*', help='Specify files to be imported')
        parser.add_argument('--lowercase', action='store_true', help='True if specified, Output a lowercase csv file, hack for duplicates case-insensitivity')

    def handle(self, *args, **kwargs):
        if not type(self.options) == dict: # pragma: no cover
            raise Exception("DataImportCommand must have options defined")
        # exit if nothing specified
        if all(kwargs[option] is None for option in self.options): # pragma: no cover
            print(f"Please specify one or more of: {', '.join(f'--{option} <file>' for option in self.options)}")
            exit()
        # exit if one of the options has no files specified
        if any(kwargs[option] is not None and len(kwargs[option]) < 1 for option in self.options): # pragma: no cover
            print(f"No file arguments found for: {', '.join(f'--{option} <file>' for option in self.options if kwargs[option] is not None and len(kwargs[option]) < 1)}")
            exit()
        # for each custom option
        for option, import_options in self.options.items():
            # count number of records imported
            imported = 0
            # skip
            if kwargs[option] is None: # pragma: no cover
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
                df = DataImportCommand.load_table(file, header=import_options['header_row'], dataframe=True, disallow_excel=True, csv_to_lowercase='lowercase' in kwargs)
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

    @staticmethod
    def load_table(file: str, header=0, dataframe=False, disallow_excel=False, csv_to_lowercase=True):
        ext = os.path.splitext(file)[1].lower()

        if ext == ".xlsx": # pragma: no cover
            if disallow_excel:
                raise Exception(f"excel imports has been disabled, please convert to csv first.")
            if header is None:
                raise Exception(f"Header Row needs to be specified with excel files!")
            df = pd.read_excel(file, index_col=None, header=header)
        elif ext == ".csv":
            buffer = open(file, 'r')
            if csv_to_lowercase:
                logger.info('Converting CSV to lowercase'),
                buffer = io.StringIO(buffer.read().lower())
            df = pd.read_csv(buffer, index_col=None)
        else:
            raise Exception(f"Unsupported file extension: {ext}")

        # some excel files have hidden empty columns
        df = df.filter(regex='^(?!Unnamed:).*', axis=1)
        df = df.rename(lambda s: s.lower().replace(" ", "_").replace("_/_", "_"), axis='columns')

        if ext == '.xlsx':
            logger.info(f"Header Row ({header}): {list(str(c) for c in df.columns)}")

        logger.info(f"Loaded: {len(df)} records from {file}")

        return df if dataframe else df.to_dict()

    @staticmethod
    def load_tables(files: List[str], merged=False, header=0, dataframe=False, disallow_excel=False, csv_to_lowercase=True):
        # load and merge/append tables together
        records, total = None if merged else [], 0
        for file in files:
            logger.info(f"Loading: {file}")
            assert os.path.isfile(file)
            temp = DataImportCommand.load_table(file, header=header, dataframe=dataframe, disallow_excel=disallow_excel, csv_to_lowercase=csv_to_lowercase)
            total += len(temp)
            records = temp if records is None and merged else records.append(temp)  # merge/append

        logger.info(f"Loaded: {total} records from {len(files)} files")
        return records

    @staticmethod
    def save_table(path: str, df: Union[List[dict], pd.DataFrame], to_lowercase=True):
        if type(df) is dict:
            df = pd.DataFrame(df)

        ext = os.path.splitext(path)[1].lower()
        if ext == ".csv":
            buffer = io.StringIO()
            df.to_csv(buffer, header=True, index=False)
            buffer.seek(0)
            with open(path, 'rw') as file:
                if to_lowercase:
                    logger.info('Converting to lowercase CSV'),
                file.write(buffer.read().lower() if to_lowercase else buffer.read())
        else:
            raise Exception(f"Unsupported file extension: {ext}")
