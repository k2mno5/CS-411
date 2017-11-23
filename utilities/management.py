# system dependency
from __future__ import unicode_literals
import logging
import time
import django.db.models
from django.http import HttpResponse

# datebase dependency
from . import models as StackQuora
from django.db.models import Max
from random import randint
from django.core.exceptions import ObjectDoesNotExist

# date processing dependency
from django.core import serializers
from django.http import JsonResponse
import time
import datetime
import json

# logger for management module
stdlogger = logging.getLogger(__name__)

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# ================= Functions and APIs ====================

# getFollowingStatus
# 	Function to check if one user is following other users specified in targets
# param:	uID	: an integer of the user to check its following status
#		targets	: a list of integer contains uIDs for checking if they are followed
# return:	res	: a list of 0 or 1 indicating if the target is being followed (0: no; 1: yes)
# note:
#	If the userID is invalid (not in the database), res will be a list of all 0s
#	If an userID in targets is invalid, corresponding slot in res will be 0

def getFollowingStatus(uID, targets):
    # prepare WHERE clause
    where = " WHERE uid = {} and (".format(uID)
    for targetID in targets:
        where += " uidfollowing = {} or ".format(targetID)
    where += " true = false)" # "true = false" to handle the tailing or

    # raw SQL query
    query = "SELECT * FROM Following" + where

    status = StackQuora.Following.objects.raw(query)

    res = []
    for targetID in targets:
        if any(tup.uidfollowing == targetID for tup in status):
            res.append(1)
        else:
            res.append(0)
    return res

def getVoteStatus(uID, qIDs, aIDs):
    # prepare WHERE clause
    where = " WHERE uid = {} and (".format(uID)
    for qID in qIDs:
        where += " (actionid = {} and (actiontype = {} or actiontype = {})) or ".format(qID, 2, 4)
    for aID in aIDs:
        where += " (actionid = {} and (actiontype = {} or actiontype = {})) or ".format(aID, 3, 5)
    where += " true = false)" # "true = false" to handle the tailing or

    # raw SQL query
    query = "SELECT * FROM ActivityHistory" + where

    status = StackQuora.Activityhistory.objects.raw(query)

    qRes = []
    aRes = []
    for qID in qIDs:
        found = False
        for res in status:
            if res.actionid == qID:
                if res.actiontype == 2 or res.actiontype == 4:
                    found = True
                    if res.actiontype == 2:
                        qRes.append(1)
                    else:
                        qRes.append(-1)
                    break
        if not found:
            qRes.append(0)

    for aID in aIDs:
        found = False
        for res in status:
            if res.actionid == aID:
                if res.actiontype == 3 or res.actiontype == 5:
                    found = True
                    if res.actiontype == 3:
                        aRes.append(1)
                    else:
                        aRes.append(-1)
                    break
        if not found:
            aRes.append(0)


    return qRes, aRes


def getUserActivities(uIDs, numOfPost=10, pageOffset=0, showDownVote=True):
    actionRange = 3
    if showDownVote:
        actionRange = 5
    activities = StackQuora.Activityhistory.objects.filter(uid__in = uIDs, actiontype__lte = actionRange).order_by('-time')[pageOffset*numOfPost:(pageOffset+1)*numOfPost]

    res = {"uIDs":[], "recentActivities":[]}
    for activity in activities:
        res["uIDs"].append(activity.uid)
        res["recentActivities"].append({"postID":activity.actionid, "postType":activity.actiontype%2, "actionType":activity.actiontype/2, "time":activity.time.strftime(TIME_FORMAT)})

    return res

def getUserStatus(uID, showActivities):
    userStatus = None
    try:
        userStatus = StackQuora.Users.objects.get(uid = uID)
    except ObjectDoesNotExist:
        return None


    res = {"userName":userStatus.username, "following":userStatus.following, "follower":userStatus.follower, "reputation":userStatus.reputation, "lastLogin": userStatus.lastlogin.strftime(TIME_FORMAT)}

    if showActivities:
        userActivities = getUserActivities([uID])
        res["recentActivities"] = userActivities["recentActivities"]

    return res
        
def getFollowingActivities(uID, page):
    try:
        StackQuora.Users.objects.get(uid = uID)
    except ObjectDoesNotExist:
        return None

    following = StackQuora.Following.objects.filter(uid = uID)
    followingUIDs = []
    for relation in following:
        followingUIDs.append(relation.uidfollowing)

    res = getUserActivities(followingUIDs, pageOffset = page, showDownVote = False)
    return res


def getFollows(uID, pageOffset, following, showDetail, numOfUsers = 20):
    uIDs = []
    follows = None
    if following:
        follows = StackQuora.Following.objects.filter(uid = uID).order_by('uidfollowing')[pageOffset*numOfUsers:(pageOffset+1)*numOfUsers]
    else:
        follows = StackQuora.Following.objects.filter(uidfollowing = uID).order_by('uid')[pageOffset*numOfUsers:(pageOffset+1)*numOfUsers]

    for follow in follows:
        if follow.uid == uID:
            uIDs.append(follow.uidfollowing)
        else:
            uIDs.append(follow.uid)

    res = {'uIDs': uIDs}
    if showDetail:
        res['userStatus'] = []
        for ID in uIDs:
            detail = getUserStatus(ID, False)
            res['userStatus'].append(detail)
    return res

