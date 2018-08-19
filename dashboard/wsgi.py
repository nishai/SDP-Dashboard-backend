"""
WSGI config for dashboard project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# default settings to use - also set in manage.py
os.environ.setdefault('DASHBOARD_DEVELOP', 'true')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "dashboard.settings.development" if os.environ.get("DASHBOARD_DEVELOP") == "true" else "dashboard.settings.production")

application = get_wsgi_application()
