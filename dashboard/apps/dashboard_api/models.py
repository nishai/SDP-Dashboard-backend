from django.db import models


# Table for student personal information
# Foreign key to program_code in ProgramInfo
class StudentInfo(models.Model):
	encrypted_student_no = models.PositiveSmallIntegerField(primary_key=True)
	nationality_short_name = models.CharField(max_length=255)
	home_language_description = models.CharField(max_length=30)
	race_description = models.CharField(max_length=30)
	gender = models.CharField(max_length=1)
	age = models.IntegerField()
	secondary_school_quintile = models.PositiveSmallIntegerField()
	urban_rural_secondary_school = models.CharField(max_length=10)
	secondary_school_name = models.CharField(max_length=255)
	program_code = models.ForeignKey('ProgramInfo', on_delete=models.PROTECT)
	
# Table for program (i.e BSc General) info
class ProgramInfo(models.Model):
	program_code = models.CharField(max_length=5, primary_key=True)
	program_title = models.CharField(max_length=255)

# Stats of a student in a certain course in a certain year
# Foreign keys to student_number in StudentInfo
class CourseStats(models.Model):
	course_code = models.CharField(max_length=8)
	calendar_instance_year = models.CharField(max_length=4)
	student_number = models.ForeignKey('StudentInfo', on_delete=models.CASCADE)
	year_of_study = models.PositiveSmallIntegerField	# Refers to YOS student is registered for
														# within this course year
	final_mark = models.DecimalField(max_digits=6, decimal_places=3)
	final_grade = models.CharField(max_length=5)
	progress_outcome_type = models.CharField(max_length=10)
	award_grade = models.CharField(max_length=2)

class AverageYearMarks(models.Model):
	year_of_study = models.PositiveSmallIntegerField	# Refers to YOS student is registered for
	student_number = models.ForeignKey('StudentInfo', on_delete=models.CASCADE)
	average_marks = models.DecimalField(max_digits=6, decimal_places=3)
