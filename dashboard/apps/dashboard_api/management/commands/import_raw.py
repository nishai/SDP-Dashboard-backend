import logging
from dashboard.apps.dashboard_api.management.util.base_commands import DataImportCommand
from dashboard.apps.dashboard_api.management.util.inserter import Inserter
from dashboard.apps.dashboard_api.models import RawStudentModel

logger = logging.getLogger('debug-import')


class Command(DataImportCommand):
    help = 'Imports raw stats from Wits excel stat files into the database'
    header_row = 5

    def import_table(self, df):
        logger.info(f"Importing RawStudentModel:")
        return Inserter(RawStudentModel).insert(df)
