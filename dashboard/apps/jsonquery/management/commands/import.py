from dashboard.apps.jsonquery.management.util.base_commands import DataImportCommand
from dashboard.apps.jsonquery.models import *
import logging

logger = logging.getLogger('debug-import')


class Command(DataImportCommand):
    help = 'Imports stats from Wits excel stat files (or schools+faculty+course files) into the database in a normalised form.' \
           '\nThe files can be excel or csv.' \
           '\n  - Import Or`s :' \
           '\n      "$ python3 manage.py import --or_schools schools_1.xlsx schools_2.csv --or_wits data_1.xlsx data_2.csv"' \
           '\n  - Import Nan`s:' \
           '\n      "$ python3 manage.py convert --file data_1.xlsx --out all.csv --limit 10 100 1000 -1"'

    options = {
        'or_schools': {
            'header_row': 0,
            'models': [                 # -NEW-     # -OLD-
                SchoolInfo,             # 26        # 27        (diff)
                CourseInfo,             # 1031      # 1031
            ],
        },
        'or_wits': {
            'header_row': 5,
            'depends_on': ['or_schools'],
            'models': [                 # -NEW-     # -OLD-
                ProgramInfo,            # 14        # 14
                StudentInfo,            # 16487     # 16487
                CourseStats,            # 206139    # 206139
                ProgressDescription,    # 26        # 26
                AverageYearMarks,       # 34270     # 34270
                YearOfStudy,            # 34270     # 34270
                StudentPrograms,        # 34272     # 34272
            ],
        },
        'schools': {
            'header_row': 0,
            'models': [                 # -NEW-
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
            'depends_on': ['schools'],
            'models': [                 # -NEW-
                Program,                # 14
                ProgressOutcome,        # 26
                SecondarySchool,        # 2720
                Student,                # 16487
                EnrolledYear,           # 34272     # Replaces: AverageYearMarks, YearOfStudy, StudentPrograms
                EnrolledCourse,         # 206139
            ],
        },
        'raw': {
            'header_row': 5,
            'models': [
                RawStudentModel,
            ],
        },
    }
