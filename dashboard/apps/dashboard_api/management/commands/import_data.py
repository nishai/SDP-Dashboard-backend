from dashboard.apps.dashboard_api.management.util.file_import_command import FileImportCommand
from dashboard.apps.dashboard_api.management.util.inserter import Inserter
from dashboard.apps.dashboard_api.models import *
import logging

logger = logging.getLogger('debug-import')


class Command(FileImportCommand):
    help = 'Imports stats from Wits excel stat files into the database in a normalised form'

    def import_table(self, df):
        logger.warning("SchoolInfo needs to be imported separately first.")  # TODO: where do we obtain this data?
        import_models = [
            CourseInfo,
            ProgramInfo,
            StudentInfo,
            CourseStats,
            ProgressDescription,
            AverageYearMarks,  # TODO: fix failure on more than one import due to the unique constraint
            YearOfStudy,
            StudentPrograms,
        ]
        logger.info(f"Importing {len(import_models)} tables:")
        return sum(Inserter(model).insert(df) for model in import_models)
