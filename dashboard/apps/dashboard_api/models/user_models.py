import uuid as uuid
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from rest_framework.fields import JSONField


class UserReport(models.Model):
    uuid = models.CharField(max_length=64, default=uuid.uuid1, primary_key=True, editable=False)
    # foreign
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)
    # data
    name = models.CharField(max_length=256)
    desc = models.CharField(max_length=4096)
    # meta
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Table for storing user reports"


# Table for matching schools to faculties
class ReportChart(models.Model):
    uuid = models.CharField(max_length=64, default=uuid.uuid1, primary_key=True, editable=False)
    # foreign
    report = models.ForeignKey(UserReport, editable=False, on_delete=models.CASCADE)
    # data
    name = models.CharField(max_length=256, default="")
    desc = models.CharField(max_length=4096, default="")
    data = JSONField(default=lambda: {'type': None})
    # meta
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    order_index = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = "Table for report charts"
