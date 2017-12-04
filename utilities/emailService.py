from . import models as StackQuora
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from string import Template

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import time
import re


SENDER = 'stackquora@gmail.com'
PASSWORD = '44ace411'

HOST = 'smtp.gmail.com'
PORT = 587
#s.quit()

REPLY_URL = 'http://fa17-cs411-44.cs.illinois.edu/utilities/emailService/confirm/'

GENERAL_TEMPLATE = 'Hi ${USER_NAME},<br/><br/>${CONTENT}<br/><br/>Sincerely,<br/>StackQuora Team'

VERIFICATION_TEMPLATE = 'You received this email as the last step to get everything set up, please click on the link below to finish the process.<br/><br/><a href="${GENERATED_URL}">${GENERATED_URL}</a>'

UPDATE_ON_POST = '${USER_NAME} just ${ACTION} you on question ${QUESTION_TITLE}:<br/><br/>${ANSWER_CONTENT}'

def startSession(s, email):
    #s.connect()
    s.starttls()
    s.login(SENDER, PASSWORD)
    msg = MIMEMultipart()
    msg['From'] = SENDER
    msg['To'] = email
    return msg

def endSession(s, msg, end=True):
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    if end:
        s.quit()
        del msg

def sendVerificationEmail(email, userID, userName, pendingPassword):
    try:
        s = smtplib.SMTP(host=HOST, port=PORT)
        msg = startSession(s, email)
        msg['Subject'] = "[StackQuora] Hello from StackQuora"
        url = REPLY_URL + str(userID) + '/' + hex(abs(hash(pendingPassword)^hash(userName)))[2:]
        content = Template(VERIFICATION_TEMPLATE).substitute(GENERATED_URL = url)
        message = Template(GENERAL_TEMPLATE).substitute(USER_NAME = userName, CONTENT = content)
        msg.attach(MIMEText(message,'html'))
        endSession(s, msg)
        return {'status':0, 'message':''}
    except Exception as e:
        return {'status':1, 'message':str(e)}

def receiveVerificationResponse(userID, encodedValue):
    try:
        user = StackQuora.Authorization.objects.get(uid = userID)
        userName = StackQuora.Users.objects.get(uid = userID)
        if hex(abs(hash(user.pendingpassword)^hash(userName.username)))[2:] == encodedValue:
            user.password = user.pendingpassword
            user.save()
            return {'status':0, 'message':''}
        else:
            return {'status':1, 'message':''}
    except ObjectDoesNotExist:
        return {'status':2, 'message':str(e)}
    except Exception as e:
        return {'status':3, 'message':str(e)}
        


# updateNotification, a function that can be called when there is new answer posted
# params: uid, userID of question owner
#         title, the title of the question
#         content, the content of the answer
#         answererID, userID of answer owner
# return: dictionary contains 'status' and 'message'
#             'status': 0 on success, 1 on any error
#             'message': empty string on success, error message on any error
def updateNotification(uid, title, content, answererID):
    try:
        # processing content and other parameters to get users involved
        mentioned = re.findall(r"@(\w+) ", content)
        users = StackQuora.Users.objects.filter(Q(uid__in = [uid, answererID]) | Q(username_in = mentioned))
        asker = None
        answerer = None
        mentioned = []
        mentionedUserName = {}
        for actor in users:
            if actor.uid == uid:
                asker = actor
            elif actor.uid == answererID:
                answerer = actor
            else:
                mentioned.append(actor.uid)
                mentionedUserName[actor.uid] = actor.username

        # users that are mentioned in the post
        mentionedUsers = [(mentionedUser.uid, mentionedUser.email) for mentionedUser in StackQuora.Authorization.objects.filter(uid__in = mentioned)]
        # user that gets answers (question owner)
        user = StackQuora.Authorization.objects.get(uid = uid)

        # initiate the session
        s = smtplib.SMTP(host=HOST, port=PORT)
        msg = startSession(s, user.email)
 
        # send "mentioned" email
        msg['Subject'] = "[StackQuora] You Are Mentioned"
        for user in mentionedUsers:
            msg['To'] = user[1]
            content = Template(UPDATE_ON_POST).substitute(USER_NAME = answerer.username, ACTION = "mentioned", QUESTION_TITLE = title, ANSWER_CONTENT = content)
            message = Template(GENERAL_TEMPLATE).substitute(USER_NAME = mentionedUserName[user[0]], CONTENT = content)
            msg.attach(MIMEText(message,'html'))
            endSession(s, msg, False)

        # send update to question owner
        msg['Subject'] = "[StackQuora] Update on Your Question"
        msg['To'] = user.email
        content = Template(UPDATE_ON_POST).substitute(USER_NAME = answerer.username, ACTION = "answered", QUESTION_TITLE = title, ANSWER_CONTENT = content)
        message = Template(GENERAL_TEMPLATE).substitute(USER_NAME = asker.username, CONTENT = content)
        msg.attach(MIMEText(message,'html'))
        endSession(s, msg)
       
        return {'status':0, 'message':''}
    except Exception as e:
        return {'status':1, 'message':str(e)}

