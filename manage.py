#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':

    if not sys.version_info[:2] >= (3, 6):
        raise RuntimeError(
            "Invalid python version: " + str(sys.version_info[:3]) + " "
                                                                     "Must be using 3.6 or above. "
                                                                     "Did you forget to activate a virtual environment?"
        )

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.common")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)
