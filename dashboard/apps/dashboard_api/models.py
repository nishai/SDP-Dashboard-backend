from django.db import models


# Table for matching schools to faculties
class SchoolInfo(models.Model):
    school = models.CharField(max_length=255, primary_key=True)
    faculty = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name = "Table for matching schools to faculties"


# Table for matching courses to schools
class CourseInfo(models.Model):
    course_code = models.CharField(max_length=5, primary_key=True)
    school = models.ForeignKey('SchoolInfo', on_delete=models.CASCADE)
    course_name = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name = "Table for matching courses to schools"


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
    course_code = models.ForeignKey('CourseInfo', on_delete=models.CASCADE)
    calendar_instance_year = models.CharField(max_length=4, null=True)
    encrypted_student_no = models.ForeignKey('StudentInfo', on_delete=models.CASCADE)
    final_mark = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    final_grade = models.CharField(max_length=5, null=True)

    class Meta:
        verbose_name = "Information about a student for a course in a specific calendar year"
        unique_together = ("course_code", "calendar_instance_year", "encrypted_student_no")


# Maps progress_outcome_type codes to verbos description
class ProgressDescription(models.Model):
    progress_outcome_type = models.CharField(max_length=10, primary_key=True)
    progress_outcome_type_description = models.CharField(max_length=254)

    class Meta:
        verbose_name = "Maps progress_outcome_type codes to verbos description"


# Average mark for a student in a specific calendar year
class AverageYearMarks(models.Model):
    calendar_instance_year = models.CharField(max_length=4, null=True)
    encrypted_student_no = models.ForeignKey('StudentInfo', on_delete=models.CASCADE)
    average_marks = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    progress_outcome_type = models.ForeignKey('ProgressDescription', on_delete=models.CASCADE, null=True)
    award_grade = models.CharField(max_length=2, null=True)

    class Meta:
        verbose_name = "Average mark for a student in a specific calendar year"
        unique_together = ("calendar_instance_year", "encrypted_student_no")


# keeps track of which year of study each student is in in each calendar year
class YearOfStudy(models.Model):
    encrypted_student_no = models.ForeignKey('StudentInfo', on_delete=models.CASCADE)
    calendar_instance_year = models.CharField(max_length=4)
    year_of_study = models.CharField(max_length=5, null=True)  # Refers to YOS student is registered for within this course year

    class Meta:
        verbose_name = "keeps track of which year of study each student is in in each calendar year"
        unique_together = ("calendar_instance_year", "encrypted_student_no")


# Table for program (i.e BSc General) info
class StudentPrograms(models.Model):
    calendar_instance_year = models.CharField(max_length=4)
    program_code = models.ForeignKey('ProgramInfo', on_delete=models.CASCADE, null=True)
    encrypted_student_no = models.ForeignKey('StudentInfo', on_delete=models.CASCADE)
    degree_complete = models.BooleanField(null=True)

    class Meta:
        verbose_name = "Table to keep track of which students are enrolled in which programs for which years."
        unique_together = ("calendar_instance_year", "encrypted_student_no", "program_code")
