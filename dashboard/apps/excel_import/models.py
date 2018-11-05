from django.core.validators import MinValueValidator, MaxValueValidator, DecimalValidator
from django.db import models
from dashboard.shared.admin import admin_site_register


# ========================================================================= #
# STAT Models - Wits performance data                                       #
# Legacy Models - TODO: REMOVE                                              #
# ========================================================================= #


# School Info

# Table for matching schools to faculties
@admin_site_register
class SchoolInfo(models.Model):
    school = models.CharField(max_length=255, primary_key=True)
    faculty = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name = "Table for matching schools to faculties"


# Course Info

# Table for matching courses to schools
@admin_site_register
class CourseInfo(models.Model):
    course_code = models.CharField(max_length=5, primary_key=True)
    school = models.ForeignKey('SchoolInfo', on_delete=models.CASCADE, null=True, related_name="courses")
    course_name = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name = "Table for matching courses to schools"


# Program Info

# Table for program (i.e BSc General) info
@admin_site_register
class ProgramInfo(models.Model):
    program_code = models.CharField(max_length=5, primary_key=True)
    program_title = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name = "Program information (i.e information about BSc General Program)"


# Student Info

# Table for student personal information
# Foreign key to program_code in ProgramInfo
@admin_site_register
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


# Course Stats

# Stats of a student in a certain course in a certain year
# Foreign keys to student_number in StudentInfo
@admin_site_register
class CourseStats(models.Model):
    course_code = models.ForeignKey('CourseInfo', on_delete=models.CASCADE, related_name="course_stats")
    calendar_instance_year = models.IntegerField(null=True, validators=[MinValueValidator(1900), MaxValueValidator(2100)])
    encrypted_student_no = models.ForeignKey('StudentInfo', on_delete=models.CASCADE, related_name="course_stats")
    final_mark = models.FloatField(null=True, validators=[DecimalValidator(max_digits=6, decimal_places=3)])
    final_grade = models.CharField(max_length=5, null=True)

    class Meta:
        verbose_name = "Information about a student for a course in a specific calendar year"
        unique_together = ("course_code", "calendar_instance_year", "encrypted_student_no")


# Progress Description

# Maps progress_outcome_type codes to verbose description
@admin_site_register
class ProgressDescription(models.Model):
    progress_outcome_type = models.CharField(max_length=10, primary_key=True)
    progress_outcome_type_description = models.CharField(max_length=254)

    class Meta:
        verbose_name = "Maps progress_outcome_type codes to verbos description"


# Average Year Marks

# Average mark for a student in a specific calendar year
# TODO: this should be merged with YearOfStudy, as the uniqueness constraints are the same
@admin_site_register
class AverageYearMarks(models.Model):
    calendar_instance_year = models.IntegerField()
    encrypted_student_no = models.ForeignKey('StudentInfo', on_delete=models.CASCADE, related_name="average_year_marks")
    average_marks = models.FloatField(null=True, validators=[DecimalValidator(max_digits=6, decimal_places=3)])
    progress_outcome_type = models.ForeignKey('ProgressDescription', on_delete=models.CASCADE, null=True, related_name="average_year_marks")
    award_grade = models.CharField(max_length=2, null=True)

    class Meta:
        verbose_name = "Average mark for a student in a specific calendar year"
        unique_together = ("calendar_instance_year", "encrypted_student_no")


# Year Of Study

# keeps track of which year of study each student is in in each calendar year
# TODO: this should be merged with AverageYearMarks, as the uniqueness constraints are the same
@admin_site_register
class YearOfStudy(models.Model):
    encrypted_student_no = models.ForeignKey('StudentInfo', on_delete=models.CASCADE, related_name="years_of_study")
    calendar_instance_year = models.IntegerField()
    year_of_study = models.CharField(max_length=5, null=True)  # Refers to YOS student is registered for within this course year

    class Meta:
        verbose_name = "keeps track of which year of study each student is in in each calendar year"
        unique_together = ("calendar_instance_year", "encrypted_student_no")


# Student Programs

# Table for program (i.e BSc General) info
@admin_site_register
class StudentPrograms(models.Model):
    calendar_instance_year = models.IntegerField()
    program_code = models.ForeignKey('ProgramInfo', on_delete=models.CASCADE, related_name="student_programs")
    encrypted_student_no = models.ForeignKey('StudentInfo', on_delete=models.CASCADE, related_name="student_programs")
    degree_complete = models.BooleanField(null=True)

    class Meta:
        verbose_name = "Table to keep track of which students are enrolled in which programs for which years."
        unique_together = ("calendar_instance_year", "encrypted_student_no", "program_code")


# ========================================================================= #
# RAW Models                                                                #
# As we get the data - TODO: REMOVE                                         #
# ========================================================================= #


@admin_site_register
class RawStudentModel(models.Model):
    """
    Example Data:
    -------------
    Encrypted Student No                      =   0021D31BE03E4AB097DCF9C0C89B13BA
    Calendar Instance Year                    =   2013
    Program Code                              =   SB000
    Program Title                             =   Bachelor of  Science
    Year of Study                             =   YOS 2
    Nationality Short Name                    =   South Africa
    Home Language Description                 =   South Sotho
    Race Description                          =   Black
    Gender                                    =   F
    Age                                       =   25
    Course Code                               =   CHEM2003
    Final Mark                                =   50
    Final Grade                               =   PMP
    Progress Outcome Type                     =   PCD
    Progress Outcome Type Description         =   Permitted to proceed
    Award Grade                               =   Q         # used for 3rd years / degree completion
    Average Marks                             =   65,67
    Secondary School Quintile                 =   4
    Urban / Rural Secondary School            =   URBAN
    Secondary School Name                     =   Forte Secondary School
    """

    # fields
    encrypted_student_no = models.CharField(max_length=255, null=True)
    calendar_instance_year = models.CharField(max_length=255, null=True)
    program_code = models.CharField(max_length=255, null=True)
    program_title = models.CharField(max_length=255, null=True)
    year_of_study = models.CharField(max_length=255, null=True)
    nationality_short_name = models.CharField(max_length=255, null=True)
    home_language_description = models.CharField(max_length=255, null=True)
    race_description = models.CharField(max_length=255, null=True)
    gender = models.CharField(max_length=255, null=True)
    age = models.CharField(max_length=255, null=True)
    course_code = models.CharField(max_length=255, null=True)
    final_mark = models.CharField(max_length=255, null=True)
    final_grade = models.CharField(max_length=255, null=True)
    progress_outcome_type = models.CharField(max_length=255, null=True)
    progress_outcome_type_description = models.CharField(max_length=255, null=True)
    award_grade = models.CharField(max_length=255, null=True)
    average_marks = models.CharField(max_length=255, null=True)
    secondary_school_quintile = models.CharField(max_length=255, null=True)
    urban_rural_secondary_school = models.CharField(max_length=255, null=True)
    secondary_school_name = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name = "Raw student data as recievied from Wits"
        unique_together = ((
            'encrypted_student_no',
            'calendar_instance_year',
            'program_code',
            'program_title',
            'year_of_study',
            'nationality_short_name',
            'home_language_description',
            'race_description',
            'gender',
            'age',
            'course_code',
            'final_mark',
            'final_grade',
            'progress_outcome_type',
            'progress_outcome_type_description',
            'award_grade',
            'average_marks',
            'secondary_school_quintile',
            'urban_rural_secondary_school',
            'secondary_school_name',
        ),)
