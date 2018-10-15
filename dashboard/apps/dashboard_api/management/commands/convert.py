from django.core.management.base import BaseCommand
import os
import logging

from dashboard.apps.dashboard_api.management.util.data_util import save_table, load_tables
from dashboard.apps.dashboard_api.models import RawStudentModel

logger = logging.getLogger('debug-import')


def import_table(df):
    logger.info(f"Converting table to records")
    items = df.to_dict('records')
    items = [RawStudentModel(**item) for item in items]
    logger.info(f"Saving records")
    return len(RawStudentModel.objects.bulk_create(items))


class Command(BaseCommand):
    help = 'load (and merge) Wits excel or csv files and convert to a single csv file' \
           '\n  - Merge Two Files of school data:' \
           '\n      "$ python3 manage.py convert --file data_1.xlsx data_2.csv --header_row 0 --out all.csv"' \
           '\n  - Create testing subsets of wits student data:' \
           '\n      "$ python3 manage.py convert --file data_1.xlsx --out all.csv --header_row 5 --limit 10 100 1000 -1"'

    def add_arguments(self, parser):
        parser.add_argument('--files', dest='files', nargs='+', type=str, help='Specify files to be imported')
        parser.add_argument('--limit', dest='limit', nargs='+', type=int, help='Truncate the outputs')
        parser.add_argument('--out', dest='out', nargs=1, type=str, help='Specify the output')
        parser.add_argument('--header_row', dest='header_row', nargs=1, type=int, help='Specify the header row if it is an excel file')

    def handle(self, *args, **options):
        if options['out'] is None:
            print("--out not specified")
            exit(1)
        if options['files'] is None:
            print("--file not specified")
            exit(1)

        # load and merge/append tables together
        df = load_tables(options['files'], header=options['header_row'][0] if (options['header_row'] is not None) else None, merged=True, dataframe=True)

        # default value - save everything
        if not options['limit']:
            options['limit'] = [-1]

        # get the output extension
        partial, ext = os.path.splitext(options['out'][0])
        ext = ext.lower()

        # save one file per limit
        for limit in {min(max(-1, l), len(df)) for l in options['limit']}:
            path = f"{partial}{ext}" if limit < 0 else f"{partial}_{limit}{ext}"
            logger.info(f"Saving: {path}")
            save_table(path, df[:limit])
