from dashboard.apps.jsonquery.management.util.dataimport import DataImportCommand
from dashboard.apps.excel_import.models import *
import logging

logger = logging.getLogger('debug-import')


class Command(DataImportCommand):
    help = 'Imports stats from Wits excel stat files (or schools+faculty+course files) into the database in a normalised form.' \
           '\nThe files can be excel or csv.' \
           '\n  - Import Or`s :' \
           '\n      "$ python3 manage.py import --or_schools schools_1.xlsx schools_2.csv --or_wits data_1.xlsx data_2.csv"' \

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
        'raw': {
            'header_row': 5,
            'models': [
                RawStudentModel,
            ],
        },
    }
