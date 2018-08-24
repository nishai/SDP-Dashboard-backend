# Generated by Django 2.1 on 2018-08-24 11:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AverageYearMarks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calendar_instance_year', models.CharField(max_length=4)),
                ('average_marks', models.DecimalField(decimal_places=3, max_digits=6)),
            ],
            options={
                'verbose_name': 'Average mark for a student in a specific calendar year',
            },
        ),
        migrations.CreateModel(
            name='CourseStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_code', models.CharField(max_length=8)),
                ('calendar_instance_year', models.CharField(max_length=4)),
                ('final_mark', models.DecimalField(decimal_places=3, max_digits=6)),
                ('final_grade', models.CharField(max_length=5)),
                ('progress_outcome_type', models.CharField(max_length=10)),
                ('award_grade', models.CharField(max_length=2)),
            ],
            options={
                'verbose_name': 'Information about a student for a course in a specific calendar year',
            },
        ),
        migrations.CreateModel(
            name='ProgramInfo',
            fields=[
                ('program_code', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('program_title', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Program information (i.e information about BSc General Program)',
            },
        ),
        migrations.CreateModel(
            name='StudentInfo',
            fields=[
                ('encrypted_student_no', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('nationality_short_name', models.CharField(max_length=255)),
                ('home_language_description', models.CharField(max_length=30)),
                ('race_description', models.CharField(max_length=30)),
                ('gender', models.CharField(max_length=1)),
                ('age', models.IntegerField()),
                ('secondary_school_quintile', models.PositiveSmallIntegerField()),
                ('urban_rural_secondary_school', models.CharField(max_length=10)),
                ('secondary_school_name', models.CharField(max_length=255)),
                ('program_code', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='dashboard_api.ProgramInfo')),
            ],
            options={
                'verbose_name': 'Student personal information',
            },
        ),
        migrations.AddField(
            model_name='coursestats',
            name='student_number',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard_api.StudentInfo'),
        ),
        migrations.AddField(
            model_name='averageyearmarks',
            name='student_number',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard_api.StudentInfo'),
        ),
    ]
