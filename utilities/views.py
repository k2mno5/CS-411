# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import *
from django.http import HttpResponse
from django.http import JsonResponse

# handle json
import json
from django.core import serializers

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect

from models import Questions
from . import management
from . import emailService

import time
import logging


# Logger in view module see README to use the logger print here will not work
stdlogger = logging.getLogger(__name__)


REDIRECTION = "stackquora://fa17-cs411-44.cs.illinois.edu/?postID="

# Default view
def index(request):
    return HttpResponse("If you see this page, Apache httpd and django is running.")


# ================= Functions and APIs ====================

# updateVoteStatus wrapper
# input: Http get_request
# output: empty http response
def updateVoteStatus(request, postID, postType, userID, voteStatus):
    postID = int(postID)
    postType = int(postType)
    userID = int(userID)
    voteStatus = int(voteStatus)
    return management.updateVoteStatus(postID, postType, userID, voteStatus)

# getUserUpdate wrapper
# input uID, Http_get_request
# output: JSON file, schema on github issue
# @NOTE, in this version, 10 random questions will be return
#        to return preference related questions, change the
#        getUserUpdate_random to getUserUpdate, which will be
#        implemented later on.
def getUserUpdate_random(request):
    return management.getUserUpdate_random()

# display question answers
# input ID, possibly UID or AID, 
#       ques, specify whether a question an all of its answers will return
# output json file specified online
def displayQuestionAnswers(request, qaID, is_ques):
    return management.displayQuestionAnswers(int(qaID), int(is_ques))

# post answer, add an answer to the question
# input request containing the json file of hte answer
# output ack
# side-effect: answer piped into the database
@csrf_exempt
def postAnswer(request):
    return management.postAnswer(request.body)

@csrf_exempt
def postQuestion(request):
    return management.postQuestion(request.body)

# delete a post, could be a question or an answer
def deletePost(request, ID, is_ques):
    return management.deletePost(int(ID), int(is_ques))


# get following status by Luo
@csrf_exempt
def getFollowingStatus(request):
    try:
        jsonBody = json.loads(request.body)
    except Exception as e:
        return HttpResponseBadRequest('Fail parsing JSON: {}'.format(e))

    # check if missing fields
    if 'content' not in jsonBody or 'userID' not in jsonBody['content'] or 'target' not in jsonBody['content']:
        return HttpResponseBadRequest('Missing field')

    # check if field type match
    uID = -1
    try:
        uID = int(jsonBody['content']['userID'])

        targets = []
        for target in jsonBody['content']['target']:
            targets.append(int(target))

        try:
            res = management.getFollowingStatus(uID, targets)
            res_dict = {}
            res_dict['following_results'] = []
            for status in res:
                if status == 0:
                    res_dict['following_results'].append("n")
                else:
                    res_dict['following_results'].append("y")
            return JsonResponse(res_dict)
        except:
            HttpResponseServerError('Internal server error, please report')
    except ValueError:
        return HttpResponseBadRequest('Field type does not match')

# get vote status by luo
@csrf_exempt
def getVoteStatus(request):
    try:
        jsonBody = json.loads(request.body)
    except Exception as e:
        return HttpResponseBadRequest('Fail parsing JSON: {}'.format(e))

    # check if missing fields
    if 'content' not in jsonBody or 'userID' not in jsonBody['content'] or 'qIDs' not in jsonBody['content'] or 'aIDs' not in jsonBody['content']:
        return HttpResponseBadRequest('Missing field')

    # check if field type match
    try:
        uID = int(jsonBody['content']['userID'])

        qIDs = []
        aIDs = []
        for target in jsonBody['content']['qIDs']:
            qIDs.append(int(target))

        for target in jsonBody['content']['aIDs']:
            aIDs.append(int(target))

        try:
            qRes, aRes = management.getVoteStatus(uID, qIDs, aIDs)
            res_dict = {}
            res_dict['question_voted_status'] = []
            res_dict['answer_voted_status'] = []
            for status in qRes:
                res_dict['question_voted_status'].append(status)
            for status in aRes:
                res_dict['answer_voted_status'].append(status)
            return JsonResponse(res_dict)
        except:
            return HttpResponseServerError('Internal server error, please report')
    except ValueError:
        return HttpResponseBadRequest('Field type does not match')

def getFollowingActivities(request, userID, page):
    try:
        uID = int(userID)
        pageOffset = int(page)
        if pageOffset < 0:
            return HttpResponseBadRequest('Invalid page offset')

        try:
            res = management.getFollowingActivities(uID, pageOffset)

            if res is None:
                return HttpResponseBadRequest('Invalid user ID')
            else:
                res['page'] = pageOffset
                return JsonResponse(res)
        except:
            return HttpResponseServerError('Internal server error, please report')

    except ValueError:
        return HttpResponseBadRequest('Field type does not match')

def getUserStatus(request, userID, showActivities):
    try:
        showAct = True
        uID = int(userID)
        if int(showActivities) == 0:
            showAct = False

        try:
            res = management.getUserStatus(uID, showAct)

            if res is None:
                return HttpResponseBadRequest('Invalid user ID')
            else:
                return JsonResponse(res)
        except:
            return HttpResponseServerError('Internal server error, please report')

    except ValueError:
        return HttpResponseBadRequest('Field type does not match')

def getFollows(request, requestType, userID, page, showDetail):
    try:
        uID = int(userID)
        pageOffset = int(page)
        returnDetail = True
        if showDetail == "0":
            returnDetail = False

        try:
            res = management.getFollows(uID, pageOffset, (requestType == "followings"), returnDetail)
            res['page'] = pageOffset
            return JsonResponse(res)
        except:
            return HttpResponseServerError('Internal server error, please report')

    except ValueError:
        # this should never happend since regex makes sure that parameters can be parsed to corresponding type
        return HttpResponseBadRequest('Field type does not match')

def getCertainActivities(request, userID, postType, actionType, page):
    try:
        uID = int(userID)
        post = int(postType)
        action = int(actionType)
        pageOffset = int(page)

        try:
            res = management.getCertainActivities(uID, post, action, pageOffset)
            res['page'] = pageOffset
            return JsonResponse(res)
        except:
            return HttpResponseServerError('Internal server error, please report')

    except ValueError:
        return HttpResponseBadRequest('Field type does not match')


# update followers function, expecting a JSON input
@csrf_exempt
def updateFollowers(request):
    return management.updateFollowers(request.body)

@csrf_exempt
def updateUserInfo(request):
    return management.updateUserInfo(request.body)

@csrf_exempt
def signup(request):
    try:
        jsonBody = json.loads(request.body)
    except Exception as e:
        return HttpResponseBadRequest('Fail parsing JSON: {}'.format(e))

    # check if missing fields
    if 'email' not in jsonBody or 'password' not in jsonBody or 'userName' not in jsonBody:
        return HttpResponseBadRequest('Missing field') 

    try:
        res = management.signup(jsonBody['email'], jsonBody['password'], jsonBody['userName'])
        if res is None:
            return HttpResponseBadRequest('Email has been registered')
        else:
            return JsonResponse(res)
    except:
        return HttpResponseServerError('Internal server error, please report')


@csrf_exempt
def login(request):
    try:
        jsonBody = json.loads(request.body)
    except Exception as e:
        return HttpResponseBadRequest('Fail parsing JSON: {}'.format(e))

    # check if missing fields
    if 'email' not in jsonBody or 'password' not in jsonBody:
        return HttpResponseBadRequest('Missing field')

    try:
        res = management.login(jsonBody['email'], jsonBody['password'])
        if res['userID'] == -1:
            return HttpResponseBadRequest('User not found')
        elif res['token'] == -1:
            return HttpResponseBadRequest('Incorrect password')
        else:
            return JsonResponse(res)
    except:
        return HttpResponseServerError('Internal server error, please report')
    

@csrf_exempt
def logout(request):
    try:
        jsonBody = json.loads(request.body)
    except Exception as e:
        return HttpResponseBadRequest('Fail parsing JSON: {}'.format(e))

    # check if missing fields
    if 'userID' not in jsonBody or 'token' not in jsonBody:
        return HttpResponseBadRequest('Missing field')
    try:
        uID = int(jsonBody['userID'])
        token = int(jsonBody['token'])

        try:
            res = management.logout(uID, token)
            if res == 0:
                return HttpResponse('Logged out')
            elif res == 1:
                return HttpResponseBadRequest('User has logged out')
            else:
                return HttpResponseBadRequest('User not found')
        except:
            return HttpResponseServerError('Internal server error, please report')

    except ValueError:
        return HttpResponseBadRequest('Field type does not match')

@csrf_exempt
def reset(request):
    try:
        jsonBody = json.loads(request.body)
    except Exception as e:
        return HttpResponseBadRequest('Fail parsing JSON: {}'.format(e))

    # check if missing fields
    if 'email' not in jsonBody or 'password' not in jsonBody:
        return HttpResponseBadRequest('Missing field')

    try:
        res = management.reset(jsonBody['email'], jsonBody['password'])
        if res == 0:
            return HttpResponse('Password has been reset')
        else:
            return HttpResponseBadRequest('User not found')
    except:
        return HttpResponseServerError('Internal server error, please report')

def receiveVerificationResponse(request, userID, encodedValue):
    try:
        uid = int(userID)
        res = emailService.receiveVerificationResponse(uid, encodedValue)
        if res['status'] == 0:
            return HttpResponse('Process completed')
        elif res['status'] == 1:
            return HttpResponseBadRequest('Invalid parameters')
        elif res['status'] == 2:
            return HttpResponseBadRequest('User Not Found')
        else:
            return HttpResponseServerError('Internal server error, please report')
    except ValueError:
        return HttpResponseBadRequest('Field type does not match')
    except:
        return HttpResponseServerError('Internal server error, please report')

def redirectToApp(request, postID):
    response = HttpResponse("", status=302)
    response['Location'] = REDIRECTION + postID
    print(response['Location'])
    return response
