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
    help = 'load (and merge) Wits excel or csv files and convert to a single csv file'

    def add_arguments(self, parser):
        parser.add_argument('--files', dest='files', nargs='+', type=str, help='Specify files to be imported')
        parser.add_argument('--limit', dest='limit', nargs='+', type=int, help='Truncate the outputs')
        parser.add_argument('--out', dest='out', nargs=1, type=str, help='Specify the output')

    def handle(self, *args, **options):
        assert options['out'] is not None, "--out not specified"
        assert options['files'] is not None, "--file not specified"

        # load and merge/append tables together
        df = load_tables(options['files'], merged=True, dataframe=True)

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
