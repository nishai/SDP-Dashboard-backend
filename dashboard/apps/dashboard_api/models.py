from django.db import models

class Enrolment(models.Model):
    program_code = models.CharField(max_length=10)
    registration_status = models.CharField(max_length=30)
    course_attempt_status = models.CharField(max_length=30)
    student_number = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    calendar_instance_year = models.CharField(max_length=4)
    course_code = models.CharField(max_length=10)
    course_title = models.CharField(max_length=40)
    nqf_credit = models.IntegerField()
    supp_mark =  models.IntegerField()
    final_mark = models.IntegerField()
    final_grade = models.IntegerField()
