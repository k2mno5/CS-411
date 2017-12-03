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
 

# date processing dependency
from django.core import serializers
from django.http import JsonResponse
from . import json_parser
import json
import random
import string
from fuzzywuzzy import fuzz, process
import nltk
from nltk import stem, metrics, tokenize

stdlogger = logging.getLogger(__name__)
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def search_driver(body):
    inJson = json.loads(body)
    query = inJson['query']
    precise_output = search_questions_precise(query)
    # stdlogger.info(precise_output)

    # if we have enough question to output, the most relevant five questions
    if len(precise_output) >= 5:
        # stdlogger.info(precise_output)
        precise_output = random.sample(precise_output, 5)
    
    # but, we might be short on questions, do a fuzzy match search
    fuzzy_output_temp = search_questions_fuzzy(query, list(precise_output))

    
    # the most relevant questions come from precise list
    # the recommended questions come from the fuzzy_list
    # total question number will be limited to 10 questions
    fuzzy_output = []
    for ele in fuzzy_output_temp:
        fuzzy_output.append(ele[0:2])

    return search_json_parser(precise_output, fuzzy_output)



# precise search, return questions that has the keyword presents 
# input, a search query
# output qIDs and number of match results
# notice, this is almost like a exact match, only title that has all the
# query words will be return.
def search_questions_precise(query):

    # preprocessing query, extract individual words
    query_list_full = query.lower().split(" ")
    # query_list_full = map((lambda x: "+"+x),query_list)
    # query = " ".join(query_list_full)

    # this will only return the questions with all the keyword present
    # sometimes, this not enough, we still need to recommend some more questions
    # try the normal way for searching
    try:
        out_list =[]
        query_list_full = map((lambda x: "+"+x),query_list_full)
        query = " ".join(query_list_full)
        query_result = StackQuora.Questions.objects.filter(title__search = query)
        for result in query_result:
            out_list.append((result.qid,result.title))
        return out_list


    except:
        out_query_set_list = []
        for each_query in query_list_full:
            query_result = (StackQuora.Questions.objects.filter(title__icontains = each_query))
            out_set = set()  
            for result in query_result:
                out_set.add((result.qid, result.title))
            out_query_set_list.append(out_set)
        # stdlogger.info(out_set)

        # stdlogger.info(out_query_set_list[0])
        return set.intersection(*out_query_set_list)



stemmer = stem.PorterStemmer()
 
def normalize(s):
    words = tokenize.wordpunct_tokenize(s.lower().strip())
    return ' '.join([stemmer.stem(w) for w in words])
 
# def fuzzy_match(s1, s2):
#     return metrics.scores.edit_distance(normalize(s1), normalize(s2))



# this search is a partial search, only partailly match the words in the title
# some title may only contains one word or a few words
def search_questions_fuzzy(query, precise_output):
    # stdlogger.info("Here into this fucntion !")
    query = query.lower()
    unprocessed_list = []
    for each_query in query.split():
        query_result = StackQuora.Questions.objects.filter(title__icontains = each_query)
        for result in query_result:
            unprocessed_list.append((result.qid, result.title))
    unprocessed_list = list(set(unprocessed_list))
    
    # stdlogger.info(query)

    processed_list = []

    # here we do a fuzzy string match on the titles
    for i in range(len(unprocessed_list)):
        qid = unprocessed_list[i][0]
        unprocessed_title = unprocessed_list[i][1]
        processed_title = normalize(unprocessed_title)
        distance = fuzz.token_set_ratio(processed_title, normalize(query))
        if (qid, unprocessed_title) not in precise_output:
            stdlogger.info((qid, unprocessed_title))
            processed_list.append((qid, unprocessed_title, distance))

        # try it
        # stdlogger.info((qid, processed_title, distance))

    # sort it 
    sorted_list = sorted(processed_list,key = lambda x: x[2], reverse = True)
    return sorted_list[0:(10-len(precise_output))]


def search_json_parser(precise_list, fuzzy_list):
    JSONOutDict = {}
    JSONOutDict['relevant questions'] = []
    JSONOutDict['recommended questions'] = []
    for ele in precise_list:
        ele_dict = {}
        ele_dict['qID'] = ele[0]
        ele_dict['title'] =  ele[1]
        ques = StackQuora.Questions.objects.get(qid = int(ele[0]))
        ele_dict['body'] = ques.body
        ele_dict['upvote'] = ques.upvote
        ele_dict['downvote'] = ques.downvote
        ele_dict['owneruserid'] = ques.owneruserid
        JSONOutDict['relevant questions'].append(ele_dict)

    for ele in fuzzy_list:
        ele_dict = {}
        ele_dict['qID'] = ele[0]
        ele_dict['title'] =  ele[1]
        ques = StackQuora.Questions.objects.get(qid = int(ele[0]))
        ele_dict['body'] = ques.body
        ele_dict['upvote'] = ques.upvote
        ele_dict['downvote'] = ques.downvote
        ele_dict['owneruserid'] = ques.owneruserid
        JSONOutDict['recommended questions'].append(ele_dict)
    return JSONOutDict





