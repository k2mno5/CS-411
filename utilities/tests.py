# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

import json

from . import models as StackQuora
from . import management
from . import views

# Create your tests here.
class ManagementTestCase(TestCase):
    def setUp(self):
        return

    # a series of tests for getFollowingStatus
    # given target with any length, it should return list of 1 or 0 with the same length
    # in case of invalid input, it will simply return 0 accordingly
    # notice that input must be integer, which will be check in view module
    def testGetOneFollowingStatus(self):
        userID = 6

        isFollowing = [1]
        res = management.getFollowingStatus(userID, isFollowing)
        self.assertEqual(res, [1])

        isNotFollowing = [5]
        res = management.getFollowingStatus(userID, isNotFollowing)
        self.assertEqual(res, [0])

        invalidIndex = [7]
        res = management.getFollowingStatus(userID, invalidIndex)
        self.assertEqual(res, [0])

        emptyTarget = []
        res = management.getFollowingStatus(userID, emptyTarget)
        self.assertEqual(res, [])


    def testGetMultipleFollowing(self):
        userID = 6
        target = [1, 5, 7]
        res = management.getFollowingStatus(userID, target)
        self.assertEqual(res, [1, 0, 0])

 
    def testGetFollowingStatusInvalidCase(self):
        # invalid user ID
        userID = 7
        target = [1, 2, 3]
        res = management.getFollowingStatus(userID, target)
        self.assertEqual(res, [0, 0, 0])


    def testGetOneVoteStatus(self):
        userID = 6

        isAnswerVoted = [2]
        isAnswerNotVoted = [3]
        isAnswerInvalid = [5]
        isQuestionVoted = [2]
        isQuestionNotVoted = [1]
        isQuestionInvalid = [5]

        qRes, aRes = management.getVoteStatus(userID, isQuestionVoted, isAnswerVoted)
        self.assertEqual(qRes, [1])
        self.assertEqual(aRes, [-1])

        qRes, aRes = management.getVoteStatus(userID, isQuestionNotVoted, isAnswerNotVoted)
        self.assertEqual(qRes, [0])
        self.assertEqual(aRes, [0])

        qRes, aRes = management.getVoteStatus(userID, isQuestionInvalid, isAnswerInvalid)
        self.assertEqual(qRes, [0])
        self.assertEqual(aRes, [0])

        emptyTarget = []
        qRes, aRes = management.getVoteStatus(userID, emptyTarget, emptyTarget)
        self.assertEqual(qRes, [])
        self.assertEqual(aRes, [])


    def testGetMultipleVote(self):
        userID = 6
        qTarget = [1, 2, 5]
        aTarget = [2, 3, 5]
        qRes, aRes = management.getVoteStatus(userID, qTarget, aTarget)
        self.assertEqual(qRes, [0, 1, 0])
        self.assertEqual(aRes, [-1, 0, 0])

 
    def testGetVoteStatusInvalidCase(self):
        # invalid user ID
        userID = 7
        target = [1, 2, 3]
        qRes, aRes = management.getVoteStatus(userID, target, target)
        self.assertEqual(qRes, [0, 0, 0])
        self.assertEqual(aRes, [0, 0, 0])


class ViewTestCase(TestCase):
    def setUp(self):
        self.request = lambda: None

    def testValidGetFollowingStatus(self):
        self.request.body = json.dumps({'content':{'userID':'6', 'target':['1', '5', '7']}})
        response = views.getFollowingStatus(self.request)
        self.assertEqual(response.content, '{"following_results": ["y", "n", "n"]}')

    def testInvalidGetFollowingStatus(self):
        # field type does not match
        self.request.body = json.dumps({'content':{'userID':'abc', 'target':['1', '5', '7']}})
        response1 = views.getFollowingStatus(self.request)

        self.request.body = json.dumps({'content':{'userID':'6', 'target':['1', 'abc', '7']}})
        response2 = views.getFollowingStatus(self.request)
        self.assertEqual(response1.content, response2.content)
        self.assertEqual(response1.content, 'Field type does not match')
        self.assertEqual(response1.status_code, 400)
       
        # missing field
        self.request.body = json.dumps({'content':{'userID':'6'}})
        response = views.getFollowingStatus(self.request)
        self.assertEqual(response.content, 'Missing field')
        self.assertEqual(response.status_code, 400)


    def testValidGetVoteStatus(self):
        self.request.body = json.dumps({'content':{'userID':'6', 'qIDs':['1', '2', '5'], 'aIDs':['2', '3', '5']}})
        response = views.getVoteStatus(self.request)
        self.assertEqual(response.content, '{"question_voted_status": [0, 1, 0], "answer_voted_status": [-1, 0, 0]}')

    def testInvalidGetVoteStatus(self):
        # field type does not match
        self.request.body = json.dumps({'content':{'userID':'abc', 'qIDs':['1', '2', '5'], 'aIDs':['2', '3', '5']}})
        response1 = views.getVoteStatus(self.request)

        self.request.body = json.dumps({'content':{'userID':'6', 'qIDs':['1', '2', '5'], 'aIDs':['2', '3', 'abc']}})
        response2 = views.getVoteStatus(self.request)
        self.assertEqual(response1.content, response2.content)
        self.assertEqual(response1.content, 'Field type does not match')
        self.assertEqual(response1.status_code, 400)
       
        # missing field
        self.request.body = json.dumps({'content':{'userID':'6'}})
        response = views.getVoteStatus(self.request)
        self.assertEqual(response.content, 'Missing field')
        self.assertEqual(response.status_code, 400)
 

class UtilitiesTestCase(TestCase):
    def setUp(self):
        return

    def test_dummy_model(self):
        dir(StackQuora)
        firstUser = StackQuora.Users.objects.get(uid=1)
        self.assertEqual(firstUser.username, "Alice")
