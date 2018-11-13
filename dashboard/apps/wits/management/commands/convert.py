from django.core.management.base import BaseCommand
import os
import logging

from dashboard.apps.wits.management.util.dataimport import DataImportCommand

logger = logging.getLogger('debug-import')


class Command(BaseCommand):
    help = 'load (and merge) Wits excel or csv files and convert to a single csv file' \
           '\n  - Merge Two Files of school data:' \
           '\n      "$ python3 manage.py convert --file data_1.xlsx data_2.csv --header_row 0 --out all.csv"' \
           '\n  - Create testing subsets of wits student data:' \
           '\n      "$ python3 manage.py convert --file data_1.xlsx --out all.csv --header_row 5 --limit 10 100 1000 -1"'

    def add_arguments(self, parser):
        # https://pymotw.com/2/argparse/
        parser.add_argument('--file', dest='files', nargs='+', type=str, help='Specify files to be imported')
        parser.add_argument('--limit', dest='limits', nargs='+', type=int, help='Truncate the outputs')
        parser.add_argument('--out', dest='out', nargs=1, type=str, help='Specify the output')
        parser.add_argument('--type', dest='type', nargs=1, type=str, help='Specify the header row if it is an excel file')
        parser.add_argument('--randomize', action='store_true', help='True if specified')
        parser.add_argument('--dry', action='store_true', help='True if specified')
        parser.add_argument('--lowercase', action='store_true', help='True if specified, Output a lowercase csv file, hack for duplicates case-insensitivity')

    def handle(self, *args, **options):

        types = {
            'wits': {
                'header': 5,
                'width': 20,
            },
            'schools': {
                'header': 0,
                'width': 3,
            },
        }

        if options['files'] is None:
            print("--file not specified")
            exit(1)
        if options['out'] is None:
            print("--out not specified")
            exit(1)
        if options['type'] is None or options['type'][0] not in types:
            print("--type not specified, must be 'wits' or 'schools'")
            exit(1)

        # load and merge/append tables together
        df = DataImportCommand.load_tables(options['files'], header=types[options['type'][0]]['header'], merged=True, dataframe=True)

        if len(df.columns) != types[options['type'][0]]['width']:
            # TODO, infer type based off width, and thus obtain column names after this.
            raise Exception(f"Are you sure you specified the correct type? The number of columns found is {len(df.columns)}, there should be {types[options['type'][0]]['width']}")

        # default value - save everything
        if not options['limits']:
            options['limits'] = [-1]

        # get the output extension
        partial, ext = os.path.splitext(options['out'][0])
        ext = ext.lower()

        if 'randomize' in options:
            df = df.sample(frac=1).reset_index(drop=True)

        # save one file per limit
        for limit in {min(max(-1, l), len(df)) for l in options['limits']}:
            path = f"{partial}{ext}" if limit < 0 else f"{partial}_{limit}{ext}"
            logger.info(f"Saving: {path}")
            save_table = df[:limit] if limit >= 0 else df
            if 'dry' not in options:
                DataImportCommand.save_table(path, save_table, to_lowercase='lowercase' in options)
