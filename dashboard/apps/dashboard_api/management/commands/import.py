from dashboard.apps.dashboard_api.management.util.base_commands import DataImportCommand
from dashboard.apps.dashboard_api.models import *
import logging

logger = logging.getLogger('debug-import')


class Command(DataImportCommand):
    help = 'Imports stats from Wits excel stat files into the database in a normalised form'

    options = {
        'old_schools': {
            'header_row': 0,
            'models': [                 # -NEW-     # -OLD-
                SchoolInfo,             # 26        # 27        (diff)
                CourseInfo,             # 1031      # 1031
            ],
        },
        'old_wits': {
            'header_row': 5,
            'models': [                 # -NEW-     # -OLD-
                ProgramInfo,            # 14        # 14
                StudentInfo,            # 16487     # 16487
                CourseStats,            # 206135    # 206139    (diff)  # TODO: reimport failing unique constraint
                ProgressDescription,    # 26        # 26
                AverageYearMarks,       # 34270     # 34270             # TODO: reimport failing unique constraint
                YearOfStudy,            # 34270     # 34270             # TODO: reimport failing unique constraint
                StudentPrograms,        # 34272     # 34272             # TODO: reimport failing unique constraint
            ],
        },
        'schools': {
            'header_row': 0,
            'models': [
                Faculty,                # 5
                School,                 # 26
                Course                  # 1031
            ],
            'header_to_field': {
                'faculty': 'faculty_title',
                'school': 'school_title',
            },
        },
        'wits': {
            'header_row': 5,
            'models': [
                Program,                # 14
                ProgressOutcome,        # 26
                SecondarySchool,        # 2720
                Student,                # 16487
                EnrolledYear,           # 34272
                EnrolledCourse,         # 206135
            ],
        },
        'raw': {
            'header_row': 5,
            'models': [
                RawStudentModel,
            ],
        },
    }
