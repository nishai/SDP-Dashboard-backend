from django.db import models

class StudentInfo(models.Model):
	student_number = models.PositiveSmallIntegerField(primary_key=True)
	nationality = models.CharField(max_length=255)
	home_language = models.CharField(max_length=30)
	race = models.CharField(max_length=30)
	gender = models.CharField(max_length=1)
	age = models.IntegerField()
	secondary_school_quintile = models.PositiveSmallIntegerField()
	average_mark = models.DecimalField(max_digits=6, decimal_places=3)
	school_urban = models.CharField(max_length=10)
	school_name = models.CharField(max_length=255)
	program_code = models.ForeignKey('ProgramInfo', on_delete=models.PROTECT)
	

class ProgramInfo(models.Model):
	program_code = models.CharField(max_length=5, primary_key=True)
	program_title = models.CharField(max_length=255)

class CourseInfo(models.Model):
	course_code = models.CharField(max_length=8, primary_key=True)
	course_title = models.CharField(max_length=255)
	
class CourseStats(models.Model):
	course_code = models.ForeignKey('CourseInfo', on_delete=models.PROTECT)
	calendar_instance_year = models.CharField(max_length=4)
	student_number = models.ForeignKey('StudentInfo', on_delete=models.CASCADE)
	year_of_study = models.PositiveSmallIntegerField
	final_mark = models.DecimalField(max_digits=6, decimal_places=3)
	final_grade = models.CharField(max_length=5)
	progress_outcome_type = models.CharField(max_length=10)
	award_grade = models.CharField(max_length=2)

#	class Meta:
#		unique_together = (('course_code', 'calendar_instance_year', 'student_number'))

#course_attempt_status = models.CharField(max_length=30)
#registration_status = models.CharField(max_length=30)
#last_name = models.CharField(max_length=30)
#first_name = models.CharField(max_length=30)
#nqf_credit = models.IntegerField()
#supp_mark =  models.IntegerField()
#final_mark = models.IntegerField()
#final_grade = models.IntegerField()
