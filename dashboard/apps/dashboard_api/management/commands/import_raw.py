import logging
from dashboard.apps.dashboard_api.management.util.file_import_command import FileImportCommand
from dashboard.apps.dashboard_api.management.util.inserter import Inserter
from dashboard.apps.dashboard_api.models import RawStudentModel

logger = logging.getLogger('debug-import')


class Command(FileImportCommand):
    help = 'Imports raw stats from Wits excel stat files into the database'

    def import_table(self, df):
        logger.info(f"Importing RawStudentModel:")
        return Inserter(RawStudentModel).insert(df)
