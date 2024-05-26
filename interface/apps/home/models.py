# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Container(models.Model):
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=255)  # Placeholder for image text
    usage_time = models.DurationField()
    last_started = models.DateTimeField(auto_now_add=True)