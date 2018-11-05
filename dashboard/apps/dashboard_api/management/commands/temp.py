from pprint import pprint
from django.core.management import BaseCommand
from django.db import models

from dashboard.apps.dashboard_api.models import EnrolledCourse, CourseInfo


class Command(BaseCommand):
    help = 'Temp tests that require django to be properly started for develop mode'

    def add_arguments(self, parser):
        # parser.add_argument('--files', dest='files', nargs='+', type=str, help='Specify files to be imported')
        pass

    def handle(self, *args, **options):
        queryset = CourseInfo.objects.all().annotate(asdfasdf=models.Max('course_stats__final_mark'))
        pprint(list(queryset[:10].values()), width=200)
        queryset = CourseInfo.objects.all().annotate(asdfasdf=models.Avg('course_stats__final_mark'))
        pprint(list(queryset[:10].values()), width=200)
        queryset = CourseInfo.objects.all().annotate(asdfasdf=models.Min('course_stats__final_mark'))
        pprint(list(queryset[:10].values()), width=200)
        queryset = CourseInfo.objects.all().annotate(asdfasdf=models.Count('course_stats__final_mark'))
        pprint(list(queryset[:10].values()), width=200)
