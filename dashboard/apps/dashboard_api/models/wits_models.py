from django.core.validators import DecimalValidator
from django.db import models


# not in excel
class Faculty(models.Model):
    faculty_id = models.AutoField(primary_key=True)
    faculty_title = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Wits Faculties"
        unique_together = ("faculty_title",)


# not in excel
class School(models.Model):
    school_id = models.AutoField(primary_key=True)
    school_title = models.CharField(max_length=255)
    faculty_id = models.ForeignKey('Faculty', related_name='schools', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Wits Schools"
        unique_together = ("school_title",)


# partially in excel
class Course(models.Model):
    course_code = models.CharField(primary_key=True, max_length=5)
    # course_title = models.CharField(max_length=255, null=True) # TODO fix import
    school_id = models.ForeignKey('School', related_name='courses', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Wits Courses"
        unique_together = ("course_code",)


class Program(models.Model):
    program_code = models.CharField(primary_key=True, max_length=5)
    program_title = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name = "Wits Academic Programs)"
        unique_together = ("program_code",)


class ProgressOutcome(models.Model):
    progress_outcome_type = models.CharField(primary_key=True, max_length=10)
    progress_outcome_type_description = models.CharField(max_length=254)

    class Meta:
        verbose_name = "Wits End of Year Progress Descriptions"
        unique_together = ("progress_outcome_type",)


class SecondarySchool(models.Model):
    secondary_school_name = models.CharField(primary_key=True, max_length=255)
    secondary_school_quintile = models.CharField(max_length=5, null=True)
    urban_rural_secondary_school = models.CharField(max_length=10, null=True)

    class Meta:
        verbose_name = "Schools Students Come From"
        unique_together = ("secondary_school_name",)


class Student(models.Model):
    encrypted_student_no = models.CharField(primary_key=True, max_length=40)
    nationality_short_name = models.CharField(max_length=255, null=True)
    home_language_description = models.CharField(max_length=30, null=True)
    race_description = models.CharField(max_length=30, null=True)
    gender = models.CharField(max_length=1, null=True)
    age = models.IntegerField(null=True)
    secondary_school_name = models.ForeignKey('SecondarySchool', related_name='students', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Wits Student Personal Information"
        unique_together = ("encrypted_student_no",)


class EnrolledYear(models.Model):
    encrypted_student_no = models.ForeignKey('Student', related_name='enrolled_years', on_delete=models.CASCADE)
    program_code = models.ForeignKey('Program', related_name='enrolled_years', on_delete=models.CASCADE)
    calendar_instance_year = models.IntegerField(null=True)
    year_of_study = models.CharField(max_length=5, null=True)  # Refers to YOS student is registered for within this course year
    award_grade = models.CharField(max_length=2, null=True)    # used for 3rd years / degree completion
    average_marks = models.FloatField(null=True, validators=[DecimalValidator(max_digits=6, decimal_places=3)])
    progress_outcome_type = models.ForeignKey('ProgressOutcome', related_name='enrolled_years', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "keeps track of which year of study each student is in in each calendar year"
        unique_together = ("encrypted_student_no", "program_code", "calendar_instance_year")


class EnrolledCourse(models.Model):
    enrolled_year_id = models.ForeignKey('EnrolledYear', related_name='enrolled_courses', on_delete=models.CASCADE, null=True)
    course_code = models.ForeignKey('Course', related_name='enrolled_courses', on_delete=models.CASCADE)
    final_mark = models.FloatField(null=True, validators=[DecimalValidator(max_digits=6, decimal_places=3)])
    final_grade = models.CharField(max_length=5, null=True)

    class Meta:
        verbose_name = "Information about a student for a course in a specific calendar year"
        unique_together = ("enrolled_year_id", "course_code")


"""
FACULTY
  * Faculty Code
    Faculty Title

SCHOOL
    > FACULTY (Faculty Code)
  * School Code
    School Title

$ COURSE
    > SCHOOL (School Code)
  * Course Code                               =   CHEM2003
    Course Title

$ PROGRAM
  * Program Code                              =   SB000
    Program Title                             =   Bachelor of  Science

$ PROGRESS_DESCRIPTION
  * Progress Outcome Type                     =   PCD
    Progress Outcome Type Description         =   Permitted to proceed

$ SECONDARY_SCHOOL
    Secondary School Quintile                 =   4
    Urban / Rural Secondary School            =   URBAN
    Secondary School Name                     =   Forte Secondary School

$ STUDENT:
  * Encrypted Student No                      =   0021D31BE03E4AB097DCF9C0C89B13BA
    Nationality Short Name                    =   South Africa
    Home Language Description                 =   South Sotho
    Race Description                          =   Black
    Gender                                    =   F
    Age                                       =   25
    > SECONDARY_SCHOOL

ENROLLED_YEAR (AVERAGE_YEAR_MARKS + YEAR_OF_STUDY, but now taking into account multiple degrees)
  * > STUDENT (Encrypted Student No)
  * > PROGRAM (Program Code)
  * Calendar Instance Year                    =   2013
    Year of Study                             =   YOS 2
    Award Grade                               =   Q         # used for 3rd years / degree completion
    Average Marks                             =   65,67
    > PROGRESS_DESCRIPTION (Progress Outcome Type)

ENROLLED_COURSE (COURSE_STATS, but using ENROLLED_YEAR)
  * > ENROLLED_YEAR
  * > COURSE (Course Code)
    Final Mark                                =   50
    Final Grade                               =   PMP
"""
