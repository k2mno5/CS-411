# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template.response import TemplateResponse
from models import Tags
from random import randint
# Create your views here

def display_random(request):
    random_idx=randint(0,Tags.objects.count()-1)
    data=Tags.objects.all()[random_idx];
    return TemplateResponse(request,'/var/www/html/random_pull/templates/random_pull/random.html',{'data':data})
