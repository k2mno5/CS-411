# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Dummy(models.Model):
    value = models.IntegerField(blank=True, null=True)
