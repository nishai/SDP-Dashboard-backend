import inspect
import sys
from pprint import pprint

from django.core.management import BaseCommand
from django.db import models

from dashboard.shared.errors import VisibleError
from dashboard.shared.measure import Measure
from dashboard.shared.model import model_relations_string, get_model_relations


class Command(BaseCommand):
    help = 'Temp tests that require django to be properly started for develop mode'

    def add_arguments(self, parser):
        # parser.add_argument('--files', dest='files', nargs='+', type=str, help='Specify files to be imported')
        pass

    def handle(self, *args, **options):
        module = 'dashboard.apps.wits.models'
        clsmembers = inspect.getmembers(sys.modules[module], inspect.isclass)
        for name, cls in clsmembers:
            if getattr(cls, '__module__', '').startswith(module) and issubclass(cls, models.Model):
                print(f"\n{'=' * 100}\n{name}\n{'=' * 100}\n")
                try:
                    print("\nFOREIGN KEY RELATIONSHIPS ONLY (MANY TO ONE) (THIS TO PARENT):\n")
                    with Measure("FRN"):
                        print(model_relations_string(cls, skip_reverse_model=False, skip_foreign_model=True))
                    print("\nREVERSE RELATIONSHIPS ONLY (ONE TO MANY) (THIS TO CHILDREN):\n")
                    with Measure("REV"):
                        print(model_relations_string(cls, skip_reverse_model=True, skip_foreign_model=False))
                    print("\nDEPTH FIRST SEARCH LINK TO ALL POSSIBLE NODES:\n")
                    with Measure("DFS"):
                        print(model_relations_string(cls, skip_reverse_model=False, skip_foreign_model=False))
                    print()
                except Exception as e:
                    raise VisibleError("Failed to print hierarchy").with_traceback(e.__traceback__)

