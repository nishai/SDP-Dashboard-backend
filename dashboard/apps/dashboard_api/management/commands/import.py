from dashboard.apps.dashboard_api.management.util.base_commands import DataImportCommand
from dashboard.apps.dashboard_api.models import *
import logging

logger = logging.getLogger('debug-import')


class Command(DataImportCommand):
    help = 'Imports stats from Wits excel stat files into the database in a normalised form'

    options = {
        'old_schools': {
            'header_row': 0,
            'models': [
                SchoolInfo,
                CourseInfo,
            ],
        },
        'old_wits': {
            'header_row': 5,
            'models': [
                StudentInfo,
                CourseStats,
                ProgressDescription,
                AverageYearMarks,
                YearOfStudy,
                StudentPrograms,
            ],
        },
        'schools': {
            'header_row': 0,
            'models': [
                Faculty,
                School,
                Course
            ],
            'header_to_field': {
                'faculty': 'faculty_title',
                'school': 'school_title',
            },
        },
        'wits': {
            'header_row': 5,
            'models': [
                Program,
                ProgressOutcome,
                SecondarySchool,
                Student,
                EnrolledYear,
                EnrolledCourse,
            ],
        },
        'raw': {
            'header_row': 5,
            'models': [
                RawStudentModel,
            ],
        },
    }
