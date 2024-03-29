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
        self.maxDiff = None

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
        # test getting verbose user status
        uID = 6
        showActivities = True

        res = management.getUserStatus(uID, showActivities)
        activityRef = management.getUserActivities([uID], 10, 0, (1<<0 | 1<<1 | 1<<2))

        self.assertEquals(res, {"userName":"Aya", "following":4, "follower":0, "reputation":0, "lastLogin": "2017-11-11 21:20:00", "recentActivities": activityRef["recentActivities"]})

        # test getting simply user status
        showActivities = False
        res = management.getUserStatus(uID, showActivities)

        self.assertEquals(res, {"userName":"Aya", "following":4, "follower":0, "reputation":0, "lastLogin": "2017-11-11 21:20:00"})

    def testInvalidUserStatus(self):
        uID = 7
        self.assertEquals(management.getUserStatus(uID, True), None)
        


    # ================== getUserActivities Function ===============
    # This is internal function, thus no edge case checking, please make sure
    # to invoke it with valid parameter
    # Notice that pageOffset is not included in return value because this is known as input
    # For including it should be done at interface level
    def testUserActivities(self):
        # one user
        uIDs = [6]
        pageOffset = 0
        numOfPost = 3
        showActionType = (1<<0 | 1<<1 | 1<<2)
        res = management.getUserActivities(uIDs, numOfPost, pageOffset, showActionType)
        
        self.assertEquals(res["uIDs"], [6, 6, 6])
        self.assertEquals(res["recentActivities"], [ {'postID': 2, 'actionType': 1, 'postType': 0, 'time': '2017-11-12 12:17:51'}, {'postID': 2, 'actionType': 2, 'postType': 1, 'time': '2017-11-11 21:44:55'}, {'postID': 3, 'actionType': 0, 'postType': 1, 'time': '2017-11-11 21:31:16'}])

        # with offset
        pageOffset = 1
        res = management.getUserActivities(uIDs, numOfPost, pageOffset, showActionType)

        self.assertEquals(res["uIDs"], [6])
        self.assertEquals(res["recentActivities"], [{'postID':4, 'actionType':0, 'postType':0, 'time': '2017-11-11 21:27:39'}] )

        # with downvote filter
        pageOffset = 0
        showActionType = (1<<0 | 1<<1)
        res = management.getUserActivities(uIDs, numOfPost, pageOffset, showActionType)

        self.assertEquals(res["uIDs"], [6, 6, 6])
        self.assertEquals(res["recentActivities"], [{'postID': 2, 'actionType': 1, 'postType': 0, 'time': '2017-11-12 12:17:51'}, {'postID': 3, 'actionType': 0, 'postType': 1, 'time': '2017-11-11 21:31:16'}, {'postID': 4, 'actionType': 0, 'postType': 0, 'time': '2017-11-11 21:27:39'}])

        # multiple user
        uIDs = [1, 2, 3]
        numOfPost = 4
        res = management.getUserActivities(uIDs, numOfPost, pageOffset, showActionType)
        
        self.assertEquals(res["uIDs"], [2, 3, 2, 1])
        self.assertEquals(res["recentActivities"], [{'postID': 2, 'actionType': 1, 'postType': 1, 'time': '2017-11-11 21:44:38'}, {'postID': 2, 'actionType': 0, 'postType': 1, 'time': '2017-11-11 21:30:30'}, {'postID':1, 'actionType':0, 'postType':1, 'time': '2017-11-11 21:30:07'}, {'postID': 2, 'actionType': 0, 'postType': 0, 'time': '2017-11-11 21:25:29'}])

        # user with no activities
        uIDs = [4]
        res = management.getUserActivities(uIDs, numOfPost, pageOffset, showActionType)

        self.assertEquals(res["uIDs"], [])
        self.assertEquals(res["recentActivities"], [])

    # =================== getFollows (getFollowing & getFollower) Function ================================
    # they are essentially the same
    # TODO: For now, only use getUserStatus if showDetail is True. But this may not be efficient, let's see
    def testGetFollowingOrFollower(self):
        # simple following
        uID = 1
        following = True
        page = 0
        showDetail = False
        # TODO: should we add date as another field in following table such that we can sort the display
        #       by time? eg. the lastest following/follower is displayed first
        #       Right now we are sorting by ID to make sure the return value is determined
        followingRef = {'uIDs': [2, 3]}
        res = management.getFollows(uID, page, following, showDetail)
        self.assertEquals(res, followingRef)

        # detail following
        showDetail = True
        followingRef['userStatus'] = [{"userName": "Javis", "following": 2, "follower": 3, "reputation": 0, "lastLogin":"2017-11-11 21:16:26"}, {"userName":"Emily", "following": 2, "follower": 3, "reputation": 0, "lastLogin": "2017-11-11 21:17:04"}]
        res = management.getFollows(uID, page, following, showDetail)
        self.assertEquals(res, followingRef)

        # page to 1 (should have no record)
        page = 1
        followingRef['uIDs'] = []
        followingRef['userStatus'] = []
        res = management.getFollows(uID, page, following, showDetail)
        self.assertEquals(res, followingRef)

        # simple follower
        uID = 1
        following = False
        page = 0
        showDetail = False

        followerRef = {'uIDs':[2, 3, 6]}
        res = management.getFollows(uID, page, following, showDetail)
        self.assertEquals(res, followerRef)

        # detail follower
        showDetail = True

        followerRef['userStatus'] = [{"userName": "Javis", "following": 2, "follower": 3, "reputation": 0, "lastLogin":"2017-11-11 21:16:26"}, {"userName":"Emily", "following": 2, "follower": 3, "reputation": 0, "lastLogin": "2017-11-11 21:17:04"}, {"userName": "Aya", "following": 4, "follower": 0, "reputation": 0, "lastLogin":"2017-11-11 21:20:00"}]
        res = management.getFollows(uID, page, following, showDetail)
        self.assertEquals(res, followerRef)

        # test invalid
        uID = 7
        res = management.getFollows(uID, page, following, showDetail)
        self.assertEquals(res, {'uIDs': [], 'userStatus':[]})

        


    # ==================== getFollowingActivities Function =============================
    def testGetFollowingActivities(self):
        pageOffset = 0
        # user has following
        uID = 1
        res = management.getFollowingActivities(uID, pageOffset)

        self.assertEquals(res["uIDs"], [2, 3, 2])
        self.assertEquals(res["recentActivities"], [{'postID': 2, 'actionType': 1, 'postType': 1, 'time': '2017-11-11 21:44:38'}, {'postID': 2, 'actionType': 0, 'postType': 1, 'time': '2017-11-11 21:30:30'}, {'postID':1, 'actionType':0, 'postType':1, 'time': '2017-11-11 21:30:07'}])

        # user has no following
        uID = 4
        res = management.getFollowingActivities(uID, pageOffset)

        self.assertEquals(res["uIDs"], [])
        self.assertEquals(res["recentActivities"], [])


    # ================= getPosts Function ===========================
    def testGetPosts(self):
        postIDs = [1]
        postTypes = [0]

        ref = [{"postID": 1, "userID": 1, "author": "Alice", "reputation": 1, "body": "This post is about Python.", "upVotes": 0, "downVotes": 0, "creationDate": "2017-11-11 21:25:05"}]
        res = management.getPosts(postIDs, postTypes)
        self.assertEquals(res, ref)

    # ================= getCertainActivities Function ==============
    def testGetCertainActivities(self):
        # get all user#6's questions and answers
        ref = {'recentActivities': [{"postID":3, "postType":1, "actionType":0, "time":"2017-11-11 21:31:16"}, {"postID":4, "postType":0, "actionType":0, "time":"2017-11-11 21:27:39"}], "postDetail": [{"postID": 3, "userID": 6, "author": "Aya", "reputation": 0, "body": "Answer to the poor Java question.", "upVotes": 0, "downVotes": 0, "creationDate": "2017-11-11 21:31:16"}, {"postID": 4, "userID": 6, "author": "Aya", "reputation": 0, "body": "This post is a C question from main user.", "upVotes": 0, "downVotes": 0, "creationDate": "2017-11-11 21:27:39"}]}
        res = management.getCertainActivities(6, 2, 0, 0)
        self.assertEquals(res, ref)




class ViewTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None
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
        ref = {'userName': 'Alice', 'lastLogin': '2017-11-11 21:15:56', 'follower': 3, 'reputation': 1, 'recentActivities': [{'postID': 2, 'actionType': 0, 'postType': 0, 'time': '2017-11-11 21:25:29'}, {'postID': 1, 'actionType': 0, 'postType': 0, 'time': '2017-11-11 21:25:05'} ], 'following': 2}
        
        userID = "1"
        showActivities = "1"
        res = views.getUserStatus(self.request, userID, showActivities)
        self.assertEqual(json.loads(res.content), ref)

        # don't show activities
        reff = {'userName': 'Alice', 'lastLogin': '2017-11-11 21:15:56', 'follower': 3, 'reputation': 1, 'following': 2}
        showActivities = "0"
        ress = views.getUserStatus(self.request, userID, showActivities)
        self.assertEqual(json.loads(ress.content), reff)

    def testInvalidGetUserStatus(self):
        userID = "7"
        showActivities = "1"
        res = views.getUserStatus(self.request, userID, showActivities)
        self.assertEqual(res.content, 'Invalid User ID')
        self.assertEqual(res.status_code, 400)

        # unmatched type
        userID = "abc"
        res = views.getUserStatus(self.request, userID, showActivities)
        self.assertEqual(res.content, 'Field type does not match')
        self.assertEqual(res.status_code, 400)


    # =================== getFollowingActivities API ====================
    def testValidGetFollowingActivities(self):
        ref = {'page':0, 'uIDs':[2,3,2], 'recentActivities':[{'postID': 2, 'actionType': 1, 'postType': 1, 'time': '2017-11-11 21:44:38'}, {'postID': 2, 'actionType': 0, 'postType': 1, 'time': '2017-11-11 21:30:30'}, {'postID':1, 'actionType':0, 'postType':1, 'time': '2017-11-11 21:30:07'}]}

        userID = "1"
        page = "0"
        res = views.getFollowingActivities(self.request, userID, page)
        self.assertEqual(json.loads(res.content), ref)


    # TODO: remove unnecessary field type or valid value checking (also in other test cases)
    # since the regex in url.py has actually check the correctness (only in the case that parameters are in url)
    def testInvalidGetFollowingActivities(self):
        userID = "7"
        page = "0"
        res = views.getFollowingActivities(self.request, userID, page)
        self.assertEqual(res.content, 'Invalid User ID')
        self.assertEqual(res.status_code, 400)

        # invalid page
        page = "-2"
        res = views.getFollowingActivities(self.request, userID, page)
        self.assertEqual(res.content, 'Invalid page offset')
        self.assertEqual(res.status_code, 400)

        # unmatched type
        page = "abc"
        res = views.getFollowingActivities(self.request, userID, page)
        self.assertEqual(res.content, 'Field type does not match')
        self.assertEqual(res.status_code, 400)


    # ================= getFollows API =============================
    def testValidGetFollows(self):
        userID = "1"
        page = "0"
        showDetail = "1"
        requestType = "followings"

        ref = {'page': 0, 'uIDs': [2, 3], 'userStatus':[{"userName": "Javis", "following": 2, "follower": 3, "reputation": 0, "lastLogin":"2017-11-11 21:16:26"}, {"userName":"Emily", "following": 2, "follower": 3, "reputation": 0, "lastLogin": "2017-11-11 21:17:04"}] }
        res = views.getFollows(self.request, requestType, userID, page, showDetail)
        self.assertEquals(json.loads(res.content), ref)

    def testInvalidGetFollows(self):
        userID = "7"
        page = "0"
        showDetail = "1"
        requestType = "followers"

        ref = {"page": 0, "uIDs":[], "userStatus":[]}
        res = views.getFollows(self.request, requestType, userID, page, showDetail)
        self.assertEquals(json.loads(res.content), ref)


    # =============== getCertainActivites API ======================
    def testGetCertainActivities(self):
        res = views.getCertainActivities(self.request, "6", "2", "0", "0")

        ref = {'recentActivities': [{"postID":3, "postType":1, "actionType":0, "time":"2017-11-11 21:31:16"}, {"postID":4, "postType":0, "actionType":0, "time":"2017-11-11 21:27:39"}], "postDetail": [{"postID": 3, "userID": 6, "author": "Aya", "reputation": 0, "body": "Answer to the poor Java question.", "upVotes": 0, "downVotes": 0, "creationDate": "2017-11-11 21:31:16"}, {"postID": 4, "userID": 6, "author": "Aya", "reputation": 0, "body": "This post is a C question from main user.", "upVotes": 0, "downVotes": 0, "creationDate": "2017-11-11 21:27:39"}], 'page': 0}

        self.assertEquals(json.loads(res.content), ref)

       
 

class UtilitiesTestCase(TestCase):
    def setUp(self):
        return

    def test_dummy_model(self):
        dir(StackQuora)
        firstUser = StackQuora.Users.objects.get(uid=1)
        self.assertEqual(firstUser.username, "Alice")
