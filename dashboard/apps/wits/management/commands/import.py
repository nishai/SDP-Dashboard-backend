from dashboard.apps.wits.management.util.dataimport import DataImportCommand
from dashboard.apps.wits.models import *
import logging

logger = logging.getLogger('debug-import')


class Command(DataImportCommand):
    help = 'Imports stats from Wits excel stat files (or schools+faculty+course files) into the database in a normalised form.' \
           '\nThe files can be excel or csv.' \
           '\n  - Import Nan`s:' \
           '\n      "$ python3 manage.py convert --file data_1.xlsx --out all.csv --limit 10 100 1000 -1"'

    options = {
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
    }
