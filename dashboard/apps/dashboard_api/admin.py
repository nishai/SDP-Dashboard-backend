from django.contrib import admin
from .models import *

admin.site.register(StudentInfo)
admin.site.register(ProgramInfo)
admin.site.register(CourseInfo)
admin.site.register(CourseStats)

