# system dependency
from __future__ import unicode_literals
import logging
import time
import django.db.models
from django.http import HttpResponse
from django.http import *


# datebase dependency
from . import models as StackQuora
from django.db.models import Max
from random import randint
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection

# date processing dependency
from django.core import serializers
from django.http import JsonResponse
from django.utils import timezone
from . import json_parser
import time
import datetime
import json

import stackexchange

def nameUpdate(request):
    so = stackexchange.Site(stackexchange.StackOverflow, "ssqUNGOxV21baN6brDTfAg((")
    so.impose_throttling = True
    so.throttle_stop = False
    users = StackQuora.Users.objects.all()
    userList = []
    userDict = {}
    for user in users:
        if user.username == "Joe":
            userList.append(user.uid)
            userDict[user.uid] = user
        if len(userList) > 95:
            us = so.users(userList)
            for u in us:
                fetchUser = userDict[u.id]
                fetchUser.username = u.display_name
                fetchUser.save()
            userList = []
            userDict = {}
    us = so.users(userList)
    for u in us:
        fetchUser = userDict[u.id]
        fetchUser.username = u.display_name
        fetchUser.save()
    return HttpResponse("Done")
