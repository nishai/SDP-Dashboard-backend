from dashboard.apps.dashboard_api.management.util.base_commands import DataImportCommand
from dashboard.apps.dashboard_api.management.util.inserter import Inserter
from dashboard.apps.dashboard_api.models.wits_models import *
import logging

logger = logging.getLogger('debug-import')


class Command(DataImportCommand):
    help = 'Imports stats from Wits excel stat files into the database in a normalised form'
    header_row = 0

    def import_table(self, df):
        import_models = [
            Faculty,
            School,
            Course,
        ]
        logger.info(f"Importing {len(import_models)} tables:")
        return sum(Inserter(model).insert(df) for model in import_models)
