import inspect
import sys
from pprint import pprint
from django.core.management import BaseCommand
from django.db import models

from dashboard.apps.dashboard_api.management.util.errors import VisibleError
from dashboard.apps.dashboard_api.management.util.modelinfo import ModelInfo
from dashboard.apps.dashboard_api.models import EnrolledCourse


class Command(BaseCommand):
    help = 'Temp tests that require django to be properly started for develop mode'

    def add_arguments(self, parser):
        # parser.add_argument('--files', dest='files', nargs='+', type=str, help='Specify files to be imported')
        pass

    def handle(self, *args, **options):
        module = 'dashboard.apps.dashboard_api.models'
        clsmembers = inspect.getmembers(sys.modules[module], inspect.isclass)
        for name, cls in clsmembers:
            if getattr(cls, '__module__', '').startswith(module) and issubclass(cls, models.Model):
                print(f"\n{'=' * 100}\n{name}\n{'=' * 100}\n")
                try:
                    ModelInfo.static_print_query_tree(cls)
                except Exception as e:
                    raise VisibleError("Failed to print hierarchy").with_traceback(e.__traceback__)

