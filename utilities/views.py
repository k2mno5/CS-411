# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render


import time
import logging

# handle json
from django.core import serializers
import json

from . import management

# Create your views here.
def index(request):
    return HttpResponse("ABC")

def getFollowingStatus(request):
    jsonBody = json.loads(request.body)

    # check if missing fields
    if 'content' not in jsonBody or 'userID' not in jsonBody['content'] or 'target' not in jsonBody['content']:
        return HttpResponseBadRequest('Missing field')

    # check if field type match
    uID = -1
    try:
        uID = int(jsonBody['content']['userID'])
    except:
        return HttpResponseBadRequest('Field type does not match')

    targets = []
    for target in jsonBody['content']['target']:
        try:
            targets.append(int(target))
        except:
            return HttpResponseBadRequest('Field type does not match')

    res = management.getFollowingStatus(uID, targets)
    res_dict = {}
    res_dict['following_results'] = []
    for status in res:
        if status == 0:
            res_dict['following_results'].append("n")
        else:
            res_dict['following_results'].append("y")
    return JsonResponse(res_dict)
