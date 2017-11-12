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
