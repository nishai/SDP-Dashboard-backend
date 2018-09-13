from django.db import models

# Table for program (i.e BSc General) info
class StudentPrograms(models.Model):
	program_code = models.ForeignKey('ProgramInfo', on_delete=models.PROTECT)
	encrypted_student_no = models.ForeignKey('StudentInfo', on_delete=models.PROTECT)
	start_calendar_year = models.CharField(max_length=4, null=True)
	end_calendar_year = models.CharField(max_length=4, null=True)

	class Meta:
		verbose_name = "Table to keep track of which students are enrolled in which programs for which years."

# Table for program (i.e BSc General) info
class ProgramInfo(models.Model):
	program_code = models.CharField(max_length=5, primary_key=True)
	program_title = models.CharField(max_length=255, null=True)

	class Meta:
		verbose_name = "Program information (i.e information about BSc General Program)"

# Table for student personal information
# Foreign key to program_code in ProgramInfo
class StudentInfo(models.Model):
	encrypted_student_no = models.CharField(max_length=40, primary_key=True)
	nationality_short_name = models.CharField(max_length=255, null=True)
	home_language_description = models.CharField(max_length=30, null=True)
	race_description = models.CharField(max_length=30, null=True)
	gender = models.CharField(max_length=1, null=True)
	age = models.IntegerField(null=True)
	secondary_school_quintile = models.CharField(max_length=5, null=True)
	urban_rural_secondary_school = models.CharField(max_length=10, null=True)
	secondary_school_name = models.CharField(max_length=255, null=True)
	
	class Meta:
		verbose_name = "Student personal information"

# Stats of a student in a certain course in a certain year
# Foreign keys to student_number in StudentInfo
class CourseStats(models.Model):
	course_code = models.CharField(max_length=8)
	calendar_instance_year = models.CharField(max_length=4, null=True)
	encrypted_student_no = models.ForeignKey('StudentInfo', on_delete=models.CASCADE)
	year_of_study = models.CharField(max_length=5, null=True)	# Refers to YOS student is registered for
																# within this course year
	final_mark = models.DecimalField(max_digits=6, decimal_places=3, null=True)
	final_grade = models.CharField(max_length=5, null=True)
	progress_outcome_type = models.CharField(max_length=10, null=True)
	award_grade = models.CharField(max_length=2, null=True)

	class Meta:
		verbose_name = "Information about a student for a course in a specific calendar year"


# Average mark for a student in a specific calendar year
class AverageYearMarks(models.Model):
	calendar_instance_year = models.CharField(max_length=4, null=True)
	year_of_study = models.CharField(max_length=5, null=True)	# Refers to YOS student is registered for
																# within this course year
	encrypted_student_no = models.ForeignKey('StudentInfo', on_delete=models.CASCADE)
	average_marks = models.DecimalField(max_digits=6, decimal_places=3, null=True)

	class Meta:
		verbose_name = "Average mark for a student in a specific calendar year"
