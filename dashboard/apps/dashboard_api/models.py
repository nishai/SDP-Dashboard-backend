from django.db import models

# https://docs.djangoproject.com/en/2.1/topics/migrations/

# Encrypted Student No                      =   0021D31BE03E4AB097DCF9C0C89B13BA
# Calendar Instance Year                    =   2013
# Program Code                              =   SB000
# Program Title                             =   Bachelor of  Science
# Year of Study                             =   YOS 2
# Nationality Short Name                    =   South Africa
# Home Language Description                 =   South Sotho
# Race Description                          =   Black
# Gender                                    =   F
# Age                                       =   25
# Course Code                               =   CHEM2003
# Final Mark                                =   50
# Final Grade                               =   PMP
# Progress Outcome Type                     =   PCD
# Progress Outcome Type Description         =   Permitted to proceed
# Award Grade                               =   Q                           # used for 3rd years / degree completion
# Average Marks                             =   65,67
# Secondary School Quintile                 =   4
# Urban / Rural Secondary School            =   URBAN
# Secondary School Name                     =   Forte Secondary School

# # raw input format received from wits
# class RawStudentModel(models.Model):
#     encrypted_student_no = models.CharField(max_length=40)
#     calendar_instance_year = models.CharField(max_length=4, null=True)
#     program_code = models.CharField(max_length=5)
#     program_title = models.CharField(max_length=255, null=True)
#     year_of_study = models.CharField(max_length=5, null=True)
#     nationality_short_name = models.CharField(max_length=255, null=True)
#     home_language_description = models.CharField(max_length=30, null=True)
#     race_description = models.CharField(max_length=30, null=True)
#     gender = models.CharField(max_length=1, null=True)
#     age = models.IntegerField(null=True)
#     course_code = models.CharField(max_length=8)
#     final_mark = models.DecimalField(max_digits=6, decimal_places=3, null=True)
#     final_grade = models.CharField(max_length=5, null=True)
#     progress_outcome_type = models.CharField(max_length=10, null=True)
#     progress_outcome_type_description = models.CharField(max_length=255, null=True)
#     award_grade = models.CharField(max_length=2, null=True)
#     average_marks = models.DecimalField(max_digits=6, decimal_places=3, null=True)
#     secondary_school_quintile = models.CharField(max_length=5, null=True)
#     urban_rural_secondary_school = models.CharField(max_length=10, null=True)
#     secondary_school_name = models.CharField(max_length=255, null=True)
#
#     class Meta:
#         verbose_name = "Raw student data as recievied from Wits"


# TODO: convert values when loading
# raw input format received from wits
class RawStudentModel(models.Model):
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


# Table for program (i.e BSc General) info
class ProgramInfo(models.Model):
    program_code = models.CharField(max_length=5, primary_key=True)
    program_title = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name = "Program information (i.e information about BSc General Program)"
        unique_together = ('program_code',)


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
    program_code = models.ForeignKey('ProgramInfo', on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = "Student personal information"
        unique_together = ('encrypted_student_no',)


# Stats of a student in a certain course in a certain year
# Foreign keys to student_number in StudentInfo
class CourseStats(models.Model):
    course_code = models.CharField(max_length=8)
    calendar_instance_year = models.CharField(max_length=4, null=True)
    encrypted_student_no = models.ForeignKey('StudentInfo', on_delete=models.CASCADE)
    year_of_study = models.CharField(max_length=5, null=True)    # Refers to YOS student is registered for within this course year
    final_mark = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    final_grade = models.CharField(max_length=5, null=True)
    progress_outcome_type = models.CharField(max_length=10, null=True)
    award_grade = models.CharField(max_length=2, null=True)

    class Meta:
        verbose_name = "Information about a student for a course in a specific calendar year"
        unique_together = ('course_code', 'calendar_instance_year', 'encrypted_student_no', 'year_of_study')


# Average mark for a student in a specific calendar year
class AverageYearMarks(models.Model):
    calendar_instance_year = models.CharField(max_length=4, null=True)
    year_of_study = models.CharField(max_length=5, null=True)    # Refers to YOS student is registered for within this course year
    encrypted_student_no = models.ForeignKey('StudentInfo', on_delete=models.CASCADE)
    average_marks = models.DecimalField(max_digits=6, decimal_places=3, null=True)

    class Meta:
        verbose_name = "Average mark for a student in a specific calendar year"
        unique_together = ('calendar_instance_year', 'encrypted_student_no',)
