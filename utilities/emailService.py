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

REDIRECT_URL = 'http://fa17-cs411-44.cs.illinois.edu/utilities/redirect/'

GENERAL_TEMPLATE = 'Hi ${USER_NAME},<br/><br/>${CONTENT}<br/><br/>Sincerely,<br/>StackQuora Team'

VERIFICATION_TEMPLATE = 'You received this email as the last step to get everything set up, please click on the link below to finish the process.<br/><br/><a href="${GENERATED_URL}">${GENERATED_URL}</a>'

UPDATE_ON_POST = '${USER_NAME} just ${ACTION} you on question ${QUESTION_TITLE}:<br/><br/>${ANSWER_CONTENT}<br/><br/><a href="${GENERATED_URL}">View in StackQuora</a><br/>'

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

def sendVerificationEmail(email, userID, userName, pendingPassword, reset=0):
    try:
        s = smtplib.SMTP(host=HOST, port=PORT)
        msg = startSession(s, email)
        if reset == 0:
            msg['Subject'] = "[StackQuora] Hello from StackQuora"
        else:
            msg['Subject'] = "[StackQuora] Resetting Your Password"
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
# params: question, Questions ojbect from models.py as the question that just received an answer
#         answer, Answer object from models.py as the answer which answered the question
# return: dictionary contains 'status' and 'message'
#             'status': 0 on success, 1 on any error
#             'message': empty string on success, error message on any error
def updateNotification(question, answer):
    try:
        # prepare information
        uid = question.owneruserid
        title = question.title
        content = answer.body
        answererID = answer.owneruserid
        qid = question.qid

        # processing content and other parameters to get users involved

        # EXTREMELY HACKY WAY TO DO "JOIN" SQL IN DJANGO
        # BUT NATURAL JOIN WILL MAKE QUERY FASTER

        rawQuery = r"SELECT A.email, U.userName AS password, A.token, A.uID, A.lastActive, A.dateJoined FROM Authorization AS A NATURAL JOIN Users AS U WHERE U.userName IN "
        # put usernames that are mentioned into query constraint
        mentioned = re.findall(r"@(\w+) ", content)
        finalQuery = rawQuery + str(tuple([user.encode("utf-8") for user in mentioned]))
        # put Q&A onwer ID into constraint
        finalQuery = finalQuery + " OR A.uID IN " + str(tuple([int(uid), int(answererID)]))

        users = StackQuora.Authorization.objects.raw(finalQuery)
        asker = None
        answerer = None
        mentioned = []

        for actor in users:
            if actor.uid == uid:
                # actually username
                asker = actor.password
            elif actor.uid == answererID:
                # actually username
                answerer = actor.password
            else:
                # HACK: actually a (email, userName) pair
                mentioned.append((actor.email, actor.password))

        # user that gets answers (question owner)
        owner = None
        try:
            owner = StackQuora.Authorization.objects.get(uid = uid)
        except ObjectDoesNotExist:
            owner = None

        # redirect url
        displayUrl = REDIRECT_URL + str(qid)

        # initiate the session
        s = smtplib.SMTP(host=HOST, port=PORT)
        msg = startSession(s, "")
 
        # send "mentioned" email
        msg['Subject'] = "[StackQuora] You Are Mentioned"
        for user in mentioned:
            msg.replace_header('To', user[0])
            emailContent = Template(UPDATE_ON_POST).substitute(USER_NAME = answerer, ACTION = "mentioned", QUESTION_TITLE = title, ANSWER_CONTENT = content, GENERATED_URL = displayUrl)
            message = Template(GENERAL_TEMPLATE).substitute(USER_NAME = user[1], CONTENT = emailContent)
            msg.set_payload(MIMEText(message,'html'))
            endSession(s, msg, False)

        # send update to question owner (if the owner is registered user)
        if owner is not None:
            msg.replace_header('Subject', "[StackQuora] Update on Your Question")
            msg.replace_header('To', owner.email)
            emailContent = Template(UPDATE_ON_POST).substitute(USER_NAME = answerer, ACTION = "answered", QUESTION_TITLE = title, ANSWER_CONTENT = content, GENERATED_URL = displayUrl)
            message = Template(GENERAL_TEMPLATE).substitute(USER_NAME = asker, CONTENT = emailContent)
            msg.set_payload(MIMEText(message,'html'))
            endSession(s, msg)
        else:
            del msg
            s.quit()
       
        return {'status':0, 'message':''}
    except Exception as e:
        return {'status':1, 'message':str(e)}

