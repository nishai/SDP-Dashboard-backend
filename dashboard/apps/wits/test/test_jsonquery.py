# ========================================================================= #
# Django pytest Documentation:                                              #
#     - https://pytest-django.readthedocs.io/en/latest/helpers.html         #
#                                                                           #
# Functions that start with "test_" are pytest tests.                       #
#   - 'Arguments' to test functions are called fixtures and are generated   #
#     by pytest on the fly based on their name.                             #
#   - You can define a new fixture by annotating a function with            #
#     @pytest.fixture (The name of the func corresponds to args in a test)  #
#   - Default fixtures are defined by django-pytest... see the link above   #
# ========================================================================= #

from typing import Type

from django.db.models import Model
from django.test import TestCase
from django.core.management import call_command
from dashboard.apps.wits.models import *


# ========================================================================= #
# Helper Functions                                                          #
# ========================================================================= #


def retrieve(model: Type[Model], **filter_args):
    first = model.objects.filter(**filter_args).values().first()
    del first['id']
    return first


# ========================================================================= #
# STAT TESTS - Wits performance data                                        #
# Legacy Tests - TODO: REMOVE                                               #
# ========================================================================= #


class JsonQueryImportTestCase(TestCase):

    def setUp(self):
        pass

    def test_command_convert(self):
        self.assertEqual(
            call_command('convert', '--file', './dashboard/apps/wits/test/data/all-test-ran_100.csv', '--out', './data/test.csv', '--type', 'wits', '--limit', '10', '50', '--randomize'),
            None
        )
        self.assertEqual(
            call_command('convert', '--file', './dashboard/apps/wits/test/data/schools.csv', '--out', './data/test.csv', '--type', 'schools', '--limit', '10', '50'),
            None
        )

    def test_command_import(self):
        # check empty
        self.assertEqual(School.objects.count(), 0)
        self.assertEqual(EnrolledYear.objects.count(), 0)
        # run command
        self.assertEqual(
            call_command('import', '--wits', './dashboard/apps/wits/test/data/all-test-ran_100.csv', '--schools', './dashboard/apps/wits/test/data/schools.csv'),
            None
        )
        # check added
        count_schools, count_enroll_year = School.objects.count(), EnrolledYear.objects.count()
        self.assertGreater(count_schools, 0)
        self.assertGreater(count_enroll_year, 0)
        # run command again
        self.assertEqual(
            call_command('import', '--wits', './dashboard/apps/wits/test/data/all-test-ran_100.csv', './dashboard/apps/wits/test/data/all-test-ran_10.csv', '--schools', './dashboard/apps/wits/test/data/schools.csv'),
            None
        )
        # check nothing has been added
        self.assertEqual(School.objects.count(), count_schools)
        self.assertEqual(EnrolledYear.objects.count(), count_enroll_year)

    def test_command_hierarchy(self):
        # run command
        self.assertEqual(
            call_command('hierarchy'),
            None
        )
