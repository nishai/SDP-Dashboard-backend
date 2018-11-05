import uuid as uuid

from django.core.validators import MinValueValidator
from django.db import models
from rest_framework.fields import JSONField
from rest_framework_jwt.serializers import User

from dashboard.shared.admin import admin_site_register


# ========================================================================= #
# USER SERIALIZER                                                           #
# ========================================================================= #


# User Report

@admin_site_register
class UserReport(models.Model):
    user = models.ForeignKey(User, related_name='reports', on_delete=models.CASCADE)
    # data
    uuid = models.CharField(max_length=64, default=uuid.uuid1, primary_key=True, editable=False)
    name = models.CharField(max_length=256)
    desc = models.CharField(max_length=4096)
    # meta
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Table for storing user reports"


# User Report Charts

@admin_site_register
class ReportChart(models.Model):
    report = models.ForeignKey(UserReport, related_name='charts', editable=False, on_delete=models.CASCADE)
    # data
    uuid = models.CharField(max_length=64, default=uuid.uuid1, primary_key=True, editable=False)
    name = models.CharField(max_length=256, default="")
    desc = models.CharField(max_length=4096, default="")
    data = JSONField(default=lambda: {'type': None})
    # meta
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    order_index = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = "Table for report charts"
