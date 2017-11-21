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

def getFollowingActivities(request, userID, page):
    uID = -1
    pageOffset = -1
    try:
        uID = int(userID)
        pageOffset = int(page)
    except:
        return HttpResponseBadRequest('Field type does not match')

    if pageOffset < 0:
        return HttpResponseBadRequest('Invalid page offset')

    res = management.getFollowingActivities(uID, pageOffset)

    if res is None:
        return HttpResponseBadRequest('Invalid User ID')
    else:
        res['page'] = pageOffset
        return JsonResponse(res)

def getUserStatus(request, userID, showActivities):
    uID = -1
    showAct = True
    try:
        uID = int(userID)
        if int(showActivities) == 0:
            showAct = False
    except:
        return HttpResponseBadRequest('Field type does not match')

    res = management.getUserStatus(userID, showAct)

    if res is None:
        return HttpResponseBadRequest('Invalid User ID')
    else:
        return JsonResponse(res)


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

def getVoteStatus(request):
    jsonBody = json.loads(request.body)

    # check if missing fields
    if 'content' not in jsonBody or 'userID' not in jsonBody['content'] or 'qIDs' not in jsonBody['content'] or 'aIDs' not in jsonBody['content']:
        return HttpResponseBadRequest('Missing field')

    # check if field type match
    uID = -1
    try:
        uID = int(jsonBody['content']['userID'])
    except:
        return HttpResponseBadRequest('Field type does not match')

    qIDs = []
    aIDs = []
    for target in jsonBody['content']['qIDs']:
        try:
            qIDs.append(int(target))
        except:
            return HttpResponseBadRequest('Field type does not match')

    for target in jsonBody['content']['aIDs']:
        try:
            aIDs.append(int(target))
        except:
            return HttpResponseBadRequest('Field type does not match')


    qRes, aRes = management.getVoteStatus(uID, qIDs, aIDs)
    res_dict = {}
    res_dict['question_voted_status'] = []
    res_dict['answer_voted_status'] = []
    for status in qRes:
        res_dict['question_voted_status'].append(status)
    for status in aRes:
        res_dict['answer_voted_status'].append(status)
    return JsonResponse(res_dict)
