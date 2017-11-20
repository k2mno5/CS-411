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

    # =================== getFollowingStatus Function ========================
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


    # ==================== getVoteStatus Function ==========================
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


    # ================= getUserStatus Function ===================
    # TODO: needs user that has more than 10 activities to test if getting 10 most recent activities
    def testValidUserStatus(self):
        uID = 6
        res = management.getUserStatus(uID)
        activityRef = management.getUserActivities([uID], 10, 1, True)

        self.assertEquals(res, {"userName":"Aya", "following":4, "follower":0, "reputation":0, "lastLogin": "2017-11-11 21:20:00", "recentActivities": activityRef["recentActivities"]})


    def testInvalidUserStatus(self):
        uID = 7
        self.assertEquals(management.getUserStatus(uID), None)
        


    # ================== getUserActivities Function ===============
    # This is internal function, thus no edge case checking, please make sure
    # to invoke it with valid parameter
    def testUserActivities(self):
        # one user
        uIDs = [6]
        pageOffset = 1
        numOfPost = 3
        showDownVote = True
        res = management.getUserActivities(uIDs, numOfPost, pageOffset, showDownVote)
        
        self.assertEquals(res["uIDs"], [6, 6, 6])
        self.assertEquals(res["recentActivities"], [{'postID': 2, 'actionType': 2, 'postType': 1, 'time': '2017-11-11 21:44:55'}, {'postID': 3, 'actionType': 0, 'postType': 1, 'time': '2017-11-11 21:31:16'}, {'postID': 4, 'actionType': 0, 'postType': 0, 'time': '2017-11-11 21:27:39'}])

        # with offset
        pageOffset = 2
        res = management.getUserActivities(uIDs, numOfPost, pageOffset, showDownVote)

        self.assertEquals(res["uIDs"], [6])
        self.assertEquals(res["recentActivities"], [{'postID':4, 'actionType':0, 'postType':0, 'time': '2017-11-11 21:27:39'}] )

        # with downvote filter
        pageOffset = 1
        showDownVote = False
        res = management.getUserActivities(uIDs, numOfPost, pageOffset, showDownVote)

        self.assertEquals(res["uIDs"], [6, 6, 6])
        self.assertEquals(res["recentActivities"], [{'postID': 3, 'actionType': 0, 'postType': 1, 'time': '2017-11-11 21:31:16'}, {'postID': 4, 'actionType': 0, 'postType': 0, 'time': '2017-11-11 21:27:39'}, {'postID':4, 'actionType':0, 'postType':0, 'time': '2017-11-11 21:27:39'}])

        # multiple user
        uIDs = [1, 2, 3]
        numOfPost = 4
        res = management.getUserActivities(uIDs, numOfPost, pageOffset, showDownVote)
        
        self.assertEquals(res["uIDs"], [2, 3, 2, 1])
        self.assertEquals(res["recentActivities"], [{'postID': 2, 'actionType': 1, 'postType': 1, 'time': '2017-11-11 21:44:38'}, {'postID': 2, 'actionType': 0, 'postType': 1, 'time': '2017-11-11 21:30:30'}, {'postID':1, 'actionType':0, 'postType':1, 'time': '2017-11-11 21:30:07'}, {'postID': 2, 'actionType': 0, 'postType': 0, 'time': '2017-11-11 21:25:29'}])

        # user with no activities
        uIDs = [4]
        res = management.getUserActivities(uIDs, numOfPost, pageOffset, showDownVote)

        self.assertEquals(res["uIDs"], [])
        self.assertEquals(res["recentActivities"], [])



class ViewTestCase(TestCase):
    def setUp(self):
        self.request = lambda: None


    # ======================= getFollowingStatus API =======================
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


    # ====================== getVoteStatus API ===========================
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


    # ===================== getUserStatus API =========================
    def testValidGetUserStatus(self):
        ref = {'userName': 'Alice', 'lastLogin': '2017-11-11 21:15:56', 'follower': 3, 'reputation': 1, 'recentActivities': [{'postID': 1, 'actionType': 0, 'postType': 0, 'time': '2017-11-11 21:25:05'}, {'postID': 2, 'actionType': 0, 'postType': 0, 'time': '2017-11-11 21:25:29'}], 'following': 2}
        
        userID = "1"
        res = views.getUserStatus(self.request, userID)
        self.assertEqual(json.loads(res.content), ref)

    def testInvalidGetUserStatus(self):
        userID = "7"
        res = views.getUserStatus(self.request, userID)
        self.assertEqual(res.content, 'Invalid User ID')
        self.assertEqual(res.status_code, 400)

        # unmatched type
        userID = "abc"
        res = views.getUserStatus(self.request, userID)
        self.assertEqual(res.content, 'Field type does not match')
        self.assertEqual(res.status_code, 400)

       
 

class UtilitiesTestCase(TestCase):
    def setUp(self):
        return

    def test_dummy_model(self):
        dir(StackQuora)
        firstUser = StackQuora.Users.objects.get(uid=1)
        self.assertEqual(firstUser.username, "Alice")
