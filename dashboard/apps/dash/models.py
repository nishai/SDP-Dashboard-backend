import uuid as uuid

from django_mysql.models import JSONField

from dashboard.shared.admin import admin_site_register
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ========================================================================= #
# USER SERIALIZER                                                           #
# ========================================================================= #


def profile_raw_data_default():
    return {'defaultReport': None, 'reports': {}}

# def user_report_default_layout():
#     return []
#
# def report_chart_default_meta():
#     return {}


@admin_site_register
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    # defaultReport = models.OneToOneField('UserReport', related_name='default_profile', null=True, on_delete=models.SET_NULL)

    # hack so I can easily store everything... but high chance that something could go wrong...
    rawData = JSONField(default=profile_raw_data_default)  # , validators=[getJsonSchemaValidator(USER_DATA_SCHEMA)])


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# @admin_site_register
# class UserReport(models.Model):
#     profile = models.ForeignKey(Profile, related_name='reports', on_delete=models.CASCADE, editable=False)
#     # data
#     id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4, editable=False)
#     layout = JSONField(default=user_report_default_layout)  # , validators=[getJsonSchemaValidator(REPORT_LAYOUT_SCHEMA)])
#     name = models.CharField(max_length=256, default="Unnamed Report")
#     # meta
#     date_created = models.DateTimeField(auto_now_add=True)
#     date_modified = models.DateTimeField(auto_now=True)
#
#
# @admin_site_register
# class ReportChart(models.Model):
#     report = models.ForeignKey(UserReport, related_name='charts', editable=False, on_delete=models.CASCADE)
#     # data
#     id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=256, default="Unnamed Chart")
#     meta = JSONField(default=report_chart_default_meta)  # validators=[getJsonSchemaValidator(CHART_META_SCHEMA)])
#     # meta
#     date_created = models.DateTimeField(auto_now_add=True)
#     date_modified = models.DateTimeField(auto_now=True)
