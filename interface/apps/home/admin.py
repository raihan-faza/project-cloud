# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import Container

class ContainerAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'usage_time', 'last_started')
    search_fields = ('name', 'image')
    list_filter = ('last_started',)

admin.site.register(Container, ContainerAdmin)