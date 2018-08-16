#!/usr/bin/env python
import os
import sys

MIN_PYTHON_VERSION = (3, 7, 0)

if __name__ == '__main__':

    # check minimum python version
    (t, v) = (MIN_PYTHON_VERSION, sys.version_info[:3])
    if not v >= t:
        invalid_python_version_exception = Exception((
            "\n\tInvalid python version: %d.%d.%d\n\tMust be using %d.%d.%d or above.\n\t" +
            "Did you forget to activate a virtual environment?"
        ) % (v[0], v[1], v[2], t[0], t[1], t[2]))  # old method of formatting to prevent errors if version is wrong.
        raise invalid_python_version_exception

    # default settings to use
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.common")

    # check if django is installed
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        failed_to_import_django_exception = ImportError(
            "\n\tCouldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable?\n\tDid you "
            "forget to activate a virtual environment?"
        )
        raise failed_to_import_django_exception

    # django entry point
    execute_from_command_line(sys.argv)
