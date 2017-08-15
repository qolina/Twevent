#! /usr/bin/env python
# -*- coding: utf-8 -*-
#Location: D:\TweetyBird_Lab\src\tweetReading.py
#author: qolina
#Function: load tweets in String
#version: V2 (optimize the program to use less memory)

import os
import re
import math
import time
import json
import enchant
# from stemming.porter2 import stem
from nltk import stem

########################################################
## Define global objects.
nonEngHash = {}
legalWordHash = {}
stopwordHash = {}
userHash = {}
tweetList = []
wordHash = {} # word:wordID
wordAppHash = {} # word: wordTFHash ([tweet_id, freq])
stemWordHash = {} # stemmedword:original word hash
stemmer = stem.PorterStemmer()
wordID = 0
engDetector = enchant.Dict("en_US")
lineStringNumber = 0
illegalJsonFormatNumber = 0
legalTweetsNumber = 0
nullIDTweetsNumber = 0
nullRTTweetsNumber = 0
nullUIDTweetsNumber = 0
########################################################
## Define user and tweet's attributes. 
## Full attributes means all atts downloaded. attributes means atts may be used in our method.
## each attri correspondes to a number(attIndex)
userFullAttNames = ["id_str","screen_name","name","description",
"created_at","location","lang",
"statuses_count","favourites_count","listed_count","friends_count","followers_count",
"id","time_zone","utc_offset","is_translator","default_profile","contributors_enabled","protected","geo_enabled","verified","show_all_inline_media",
"profile_link_color","profile_background_color","profile_background_image_url","profile_use_background_image","profile_image_url_https","profile_image_url","profile_text_color","profile_sidebar_border_color","profile_background_image_url_https","default_profile_image","profile_background_tile","profile_sidebar_fill_color"]

tweet_entitiesAttNames = ["media","user_mentions","hashtags","urls"]
tweetFullAttNames = ["id_str","user_id_str","text","created_at",
"user_mentions","hashtags","urls",
"retweet_count","retweeted","favorited",
"in_reply_to_status_id_str",
"id","entity_linkified_text","media","is_rtl_tweet","truncated","source"]

userAttNames = userFullAttNames[0:12]
tweetAttNames = tweetFullAttNames[0:11]
userAttHash = {}
tweetAttHash = {}
lackAttHash = {}
uAttIndex = 0
for uAtt in userAttNames:
    userAttHash[userAttNames[uAttIndex]] = uAttIndex
    uAttIndex += 1
tAttIndex = 0
for tAtt in tweetAttNames:
    tweetAttHash[tweetAttNames[tAttIndex]] = tAttIndex
    tAttIndex += 1

########################################################
## Define class user(12) and tweet(10) with all (may) used atts.

class User:
    def __init__(self,userAtts):
        self.id_str = userAtts[userAttHash.get("id_str")]
        self.screen_name = userAtts[userAttHash.get("screen_name")]
        self.name = userAtts[userAttHash.get("name")]
        self.description = userAtts[userAttHash.get("description")]
        self.created_at = userAtts[userAttHash.get("created_at")]
        self.location = userAtts[userAttHash.get("location")]
        self.lang = userAtts[userAttHash.get("lang")]
        self.statuses_count = userAtts[userAttHash.get("statuses_count")]
        self.favourites_count = userAtts[userAttHash.get("favourites_count")]
        self.listed_count = userAtts[userAttHash.get("listed_count")]
        self.friends_count = userAtts[userAttHash.get("friends_count")]
        self.followers_count = userAtts[userAttHash.get("followers_count")]
        

class Tweet:
    def __init__(self,tweetAtts):
        self.id_str = tweetAtts[tweetAttHash.get("id_str")]
        self.user_id_str = tweetAtts[tweetAttHash.get("user_id_str")]
        self.text = tweetAtts[tweetAttHash.get("text")]
        self.created_at = tweetAtts[tweetAttHash.get("created_at")]
        #self.media = tweetAtts[tweetAttHash.get("media")]
        self.user_mentions = tweetAtts[tweetAttHash.get("user_mentions")]
        self.hashtags = tweetAtts[tweetAttHash.get("hashtags")]
        self.urls = tweetAtts[tweetAttHash.get("urls")]
        self.retweet_count = tweetAtts[tweetAttHash.get("retweet_count")]
        #self.is_rtl_tweet = tweetAtts[tweetAttHash.get("is_rtl_tweet")]
        self.retweeted = tweetAtts[tweetAttHash.get("retweeted")]
        self.favorited = tweetAtts[tweetAttHash.get("favorited")]
        self.in_reply_to_status_id_str = tweetAtts[tweetAttHash.get("in_reply_to_status_id_str")]
        #self.truncated = tweetAtts[tweetAttHash.get("truncated")]
        
    ## feature used
    def setTF_IDF_Vector(self,TF_IDF_Vector):
        self.TF_IDF_Vector = TF_IDF_Vector

## load stop words
def loadStopword(stopwordsFilePath):
    global stopwordHash
    stopFile = file(stopwordsFilePath)
    while True:
        lineStr = stopFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        lineStr = re.sub(r'\s+', " ", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        stopwordHash[lineStr] = 1
    stopFile.close()
    print "### " + str(time.asctime()) + " #" + str(len(stopwordHash)) + " stop words are loaded from " + stopwordsFilePath
########################################################
## Load users and tweets from files in directory dirPath

def loadDataFromFiles(dirPath):
    print "### " + str(time.asctime()) + " # Loading files from directory: " + dirPath
    loadDataDebug = True
    currDir = os.getcwd()
    os.chdir(dirPath)
    fileList = os.listdir(dirPath)
    fileList.sort()
    lineIdx = 0
    sinLocNum = 0
    noLocNum = 0
    otherLocNum = 0
    for item in fileList:
        if loadDataDebug:
            print "Reading from file " + ": " + item
        subFile = file(item)
        newSgpFile = file(r"/home/yxqin/twevent/data/201301Sin/sin_" + item, "w")
        while True:
            lineStr = subFile.readline()
            lineStr = re.sub(r'\n', " ", lineStr)
            lineStr = re.sub(r'\s+', " ", lineStr)
            lineStr = lineStr.strip()
            if len(lineStr) <= 0:
                break
            lineIdx += 1
            lineStr = re.sub(r'\\\\', r"\\", lineStr)
            #print "---" + str(lineIdx) + ": ",
            #print lineStr
            # compile into json format
            try:
                
                jsonObj = json.loads(lineStr)
            except ValueError as detail:
                if loadDataDebug:
                    print "Non-json format! ", detail
                continue
            
            # create tweet and user instance for current jsonObj
            currUser = getUser(jsonObj)
            currTweet = getTweet(jsonObj)
            if currTweet is None: # lack of id_str
                if loadDataDebug:
                    print "Null tweet" + str(jsonObj)
                nullIDTweetsNumber += 1
                continue
            if currUser is None: # lack of user or user's id_str
                if loadDataDebug:
                    print "Null user" + str(jsonObj)
                nullUIDTweetsNumber += 1
                continue
            
            currTweet.user_id_str = currUser.id_str # assign tweet's user_id_str
            #print "----current Tweet:" + currTweet.id_str
            #print "Before pre-process:" + currTweet.text
            
            singaporeFlag = False
            if currUser.location == "":
                noLocNum += 1
            elif currUser.location.find("singapore") >= 0:
                singaporeFlag = True
                print "---" + str(lineIdx) + ": singapore"
#                print currUser.location
            elif currUser.location.find("Singapore") >= 0:
                singaporeFlag = True
                print "---" + str(lineIdx) + ": Singapore"
#                print currUser.location
            else:
                otherLocNum += 1
            
            if singaporeFlag:
                # store
                sinLocNum +=1
                newSgpFile.write(lineStr + "\n")
        newSgpFile.close()
        
    print "Singapore users: " + str(sinLocNum)
    print "No location users: " + str(noLocNum)
    print "other location users: " + str(otherLocNum)
    
## extract a tweet for current tweetLine
def getTweet(jsonObj):
    tweetAtts = []
    if not jsonObj.has_key('id_str'):
        return None
    tweetAtts.append(jsonObj['id_str'])
    tweetAtts.append('user_id_str')# user-id will be assigned later
    tweetAtts = getValue(tweetAtts,jsonObj,'text')
    tweetAtts = getValue(tweetAtts,jsonObj,'created_at')
    #tweetAtts = getValue2(tweetAtts,jsonObj,'entities','media')
    tweetAtts = getValue2(tweetAtts,jsonObj,'entities','user_mentions')
    tweetAtts = getValue2(tweetAtts,jsonObj,'entities','hashtags')
    tweetAtts = getValue2(tweetAtts,jsonObj,'entities','urls')
    tweetAtts = getValue(tweetAtts,jsonObj,'retweet_count')
    #tweetAtts = getValue(tweetAtts,jsonObj,'is_rtl_tweet')
    tweetAtts = getValue(tweetAtts,jsonObj,'retweeted')
    tweetAtts = getValue(tweetAtts,jsonObj,'favorited')
    tweetAtts = getValue(tweetAtts,jsonObj,'in_reply_to_status_id_str')
    
    tweet = Tweet(tweetAtts)
    return tweet

## extract an user for current tweetLine
def getUser(jsonObj):
    userAtts = []
    if not jsonObj.has_key('user'):
        return None
    if not jsonObj['user'].has_key('id_str'):
        return None
    
    userAtts.append(jsonObj['user']['id_str'])
    userAtts = getValue2(userAtts,jsonObj,'user','screen_name')
    userAtts = getValue2(userAtts,jsonObj,'user','name')
    userAtts = getValue2(userAtts,jsonObj,'user','description')
    userAtts = getValue2(userAtts,jsonObj,'user','created_at')
    userAtts = getValue2(userAtts,jsonObj,'user','location')
    userAtts = getValue2(userAtts,jsonObj,'user','lang')
    userAtts = getValue2(userAtts,jsonObj,'user','statuses_count')
    userAtts = getValue2(userAtts,jsonObj,'user','favourites_count')
    userAtts = getValue2(userAtts,jsonObj,'user','listed_count')
    userAtts = getValue2(userAtts,jsonObj,'user','friends_count')
    userAtts = getValue2(userAtts,jsonObj,'user','followers_count')
    
    user = User(userAtts)
    return user

def getValue(attArr, jsonObj, keyword):
    if jsonObj.has_key(keyword):
        attArr.append(jsonObj[keyword])
    else:
        attArr.append(None)
        lackAttHash[keyword] = 1
    return attArr
    
def getValue2(attArr, jsonObj, keyword1, keyword2):
    if not jsonObj.has_key(keyword1):
        attArr.append(None)
        return attArr
    if jsonObj[keyword1].has_key(keyword2):
            attArr.append(jsonObj[keyword1][keyword2])
    else:
        attArr.append(None)
        #print "Not Found " + keyword1 + " - " + keyword2
        #statistic number of atts missed
        keyword = keyword1 + "-" + keyword2
        lackAttHash[keyword] = 1
    return attArr

########################################################
## the main Function
currDir = os.getcwd()
stopwordsFilePath = currDir + "/.." + r"/tools/stoplist.dft"
#dirPath = currDir + "/.." + r"/Data/20130101"
dirPath = r"/home/yxqin/twitter_NUS/201301_files"

print "Program starts at time:" + str(time.asctime())

loadStopword(stopwordsFilePath)
loadDataFromFiles(dirPath)
print "Program ends at time:" + str(time.asctime())
