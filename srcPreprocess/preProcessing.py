#! /usr/bin/env python
# -*- coding: utf-8 -*-
#Location: D:\Twevent\src\preProcessing.py
#author: qolina
#Function: load tweets in dir() and preProcess
#version: V1

import os
import re
import math
import time
import json
import enchant
import cPickle

########################################################
## Define global objects.
#stemWordHash = {} # stemmedword:original word hash
#stemmer = stem.PorterStemmer()

engDetector = enchant.Dict("en_US")
stopwordHash = {}
userHash = {} # calculate num of users
tweetLengHash = {} # calculate average length of tweets
wordHash = {} # calculate number of unique words
wordID = 0
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
userFullAttNames = ["id_str","created_at","location","lang",
"statuses_count","favourites_count","listed_count","friends_count","followers_count",
"screen_name","name","description","id","time_zone","utc_offset","is_translator","default_profile","contributors_enabled","protected","geo_enabled","verified","show_all_inline_media",
"profile_link_color","profile_background_color","profile_background_image_url","profile_use_background_image","profile_image_url_https","profile_image_url","profile_text_color","profile_sidebar_border_color","profile_background_image_url_https","default_profile_image","profile_background_tile","profile_sidebar_fill_color"]

tweet_entitiesAttNames = ["media","user_mentions","hashtags","urls"]
tweetFullAttNames = ["id_str","user_id_str","text","created_at",
"user_mentions","hashtags","urls",
"retweet_count","retweeted","favorited",
"in_reply_to_status_id_str","lang",
"id","entity_linkified_text","media","is_rtl_tweet","truncated","source"]

userAttNames = userFullAttNames[0:10]
tweetAttNames = tweetFullAttNames[0:13]
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
## Define class user(9) and tweet(12) with all (may) used atts.

class User:
    def __init__(self,userAtts):
        self.id_str = userAtts[userAttHash.get("id_str")]
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
        self.user_mentions = tweetAtts[tweetAttHash.get("user_mentions")]
        self.hashtags = tweetAtts[tweetAttHash.get("hashtags")]
        self.urls = tweetAtts[tweetAttHash.get("urls")]
        self.retweet_count = tweetAtts[tweetAttHash.get("retweet_count")]
        self.retweeted = tweetAtts[tweetAttHash.get("retweeted")]
        self.favorited = tweetAtts[tweetAttHash.get("favorited")]
        self.in_reply_to_status_id_str = tweetAtts[tweetAttHash.get("in_reply_to_status_id_str")]
        self.lang = tweetAtts[tweetAttHash.get("lang")]
                
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
########################################################
## preprocessing for each tweet:
## 1) delete non-Eng words (#filter out @ and url first#, filter out words contain characters except[a-z][1-9])
## 2) stop words filtering
## 3) 0-length tweet text

def loadDataFromFiles(dirPath, outputDirPath):
    print "### " + str(time.asctime()) + " # Loading files from directory: " + dirPath
    loadDataDebug = False
    preprocessDebug = False
    global userHash, wordHash, tweetLengHash
    global illegalJsonFormatNumber, legalTweetsNumber, nullIDTweetsNumber, nullUIDTweetsNumber, nullRTTweetsNumber, lineStringNumber
    currDir = os.getcwd()
    os.chdir(dirPath)
    fileList = os.listdir(dirPath)
    fileList.sort()
    lineIdx = 0
    docIndex = 0

    for item in fileList:
        docIndex += 1
        if loadDataDebug:
            print "Reading from file " + ": " + item
        subFile = file(item)
        while True:
            lineStr = subFile.readline()
            lineStr = re.sub(r'\n', " ", lineStr)
            lineStr = re.sub(r'\s+', " ", lineStr)
            lineStr = lineStr.strip()
            if len(lineStr) <= 0:
                break
            lineIdx += 1
            lineStr = re.sub(r'\\\\', r"\\", lineStr)  # especially for twitter from NUS
            
            # compile into json format
            try:
                jsonObj = json.loads(lineStr)
            except ValueError:
                if loadDataDebug:
                    print "---Non-json format!" + str(lineIdx)
                illegalJsonFormatNumber += 1
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
            
            # pre-processing
            if loadDataDebug:
                print "----current Tweet:" + currTweet.id_str
                print "Before pre-process:" + currTweet.text

            #filter out non-Eng words
            text_Eng = filter_nonEng(currTweet)
            if len(text_Eng) <= 0:
                currTweet.text = None
                if preprocessDebug:
                    print "Deleting 0-length tweet... " + currTweet.id_str
                continue
            else:
                currTweet.text = text_Eng
                if preprocessDebug:
                    print "After process:" + currTweet.text
            
            # calculate
            if currUser.id_str not in userHash:
                userHash[currUser.id_str] = 1
            wordArr = currTweet.text.split(" ");
            tweetLeng = len(wordArr)
            if tweetLeng in tweetLengHash:
                tweetLengHash[tweetLeng] += 1
            else:
                tweetLengHash[tweetLeng] = 1
            for word in wordArr: # wordHash
                if word in wordHash:
                    wordHash[word] += 1
                else:
                    wordHash[word] = 1
            
            # storing
            if legalTweetsNumber == 0:
                baseTime = readTime(currTweet.created_at)
                baseDate = time.strftime("%Y-%m-%d", baseTime)
                legalTweetsNumber += 1
                outputTweetFile = file(outputDirPath + r"tweetFile_" + inputDir_startTime + "_" + baseDate, "wb")
                outputTweetContentFile = file(outputDirPath + r"tweetContentFile_" + inputDir_startTime + "_" + baseDate, "w")
                cPickle.dump(currTweet, outputTweetFile)
                outputTweetContentFile.write(currTweet.id_str + " " + currTweet.text + "\n")
                continue
            
            if loadDataDebug:
                print "After loading: current Tweet:" + currTweet.id_str + " " + currTweet.text
            if lineIdx%10000 == 0:
                print "Log info: " + str(time.asctime()) + " # " + str(lineIdx) + " lines has been read from file" + item
            currDate = time.strftime("%Y-%m-%d", readTime(currTweet.created_at))
            if currDate < baseDate:
                print "wrong current Tweet:" + currTweet.id_str + " " + currTweet.created_at
                continue
            if currDate != baseDate:
                print "### " + outputTweetFile.name, 
                print " and " + outputTweetContentFile.name + " writing process finished! start writing next..."
                outputTweetFile = file(outputDirPath + r"tweetFile_" + inputDir_startTime + "_" + currDate, "wb")
                outputTweetContentFile = file(outputDirPath + r"tweetContentFile_" + inputDir_startTime + "_" + currDate, "w")
                baseDate = currDate
            
            cPickle.dump(currTweet, outputTweetFile)
            outputTweetContentFile.write(currTweet.id_str + " " + currTweet.text + "\n")
            legalTweetsNumber += 1

    
    lineStringNumber = lineIdx
    os.chdir(currDir)
    outputTweetFile.close()
    outputTweetContentFile.close()

def readTime(timeStr):
    #Time format in tweet: "Sun Jan 23 00:00:02 +0000 2011"
    tweetTimeFormat = r"%a %b %d %X +0000 %Y"
    createTime = time.strptime(timeStr, tweetTimeFormat)
    return createTime
    
## extract a tweet for current tweetLine
def getTweet(jsonObj):
    tweetAtts = []
    if not jsonObj.has_key('id_str'):
        return None
    tweetAtts.append(jsonObj['id_str'])
    tweetAtts.append('user_id_str')# user-id will be assigned later
    tweetAtts = getValue(tweetAtts,jsonObj,'text')
    tweetAtts = getValue(tweetAtts,jsonObj,'created_at')
    tweetAtts = getValue2(tweetAtts,jsonObj,'entities','user_mentions')
    tweetAtts = getValue2(tweetAtts,jsonObj,'entities','hashtags')
    tweetAtts = getValue2(tweetAtts,jsonObj,'entities','urls')
    tweetAtts = getValue(tweetAtts,jsonObj,'retweet_count')
    tweetAtts = getValue(tweetAtts,jsonObj,'retweeted')
    tweetAtts = getValue(tweetAtts,jsonObj,'favorited')
    tweetAtts = getValue(tweetAtts,jsonObj,'in_reply_to_status_id_str')
    tweetAtts = getValue(tweetAtts,jsonObj,'lang')
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

#filter out non-Eng words (with encoding number.)
# and stem each word
def filter_nonEng(currTweet):
#    global stemWordHash
    englishDetectDebug = False
    nonEngNum = 0
    validWordNum = 0
    hashTagList = []
    for hashtag in currTweet.hashtags:
        hashtagWord = hashtag['text']
        hashTagList.append("#"+hashtagWord)
    
    if englishDetectDebug:
        print "--------------------------------" + currTweet.id_str
        print "Before:" + currTweet.text
    
    wordArr = currTweet.text.split(" ")
    newArr = []
    for word in wordArr:
        if re.match('http',word):  # delete urls
            continue        

        # hashtag (no stem) and mention words (no stem and englishDetect)
## Bug to be fixed        # wrong order: detect @ first, then hashtag
        hashTagWordCopy = ""
        if word in hashTagList:
            hashTagWordCopy = word
            word = word[1:len(word)]
        if word.find("@") >= 0:
            word = re.sub("[^@a-zA-Z0-9]","",word)
            newArr.append(word)
            continue
        
        word = re.sub("&lt;","<", word)
        word = re.sub("&gt;",">", word)
        illegelLetter = False
        puncOnly = True
        for letter in word:
            encodeNum = ord(letter)
            if (encodeNum < 32) | (encodeNum > 126):
                illegelLetter = True
                break
            if re.match("[a-zA-Z0-9]", letter):
                puncOnly = False
        
        if illegelLetter: #contain illegel letter
            continue
        else:
            if len(hashTagWordCopy)>1: # if hashtag word contains illegal letter, remove it
                newArr.append(hashTagWordCopy)
                continue
        if puncOnly: # only contain punctuations
            continue

        if re.findall("[^a-zA-Z0-9]", word): # contain some punctuations
            word = re.sub("^[^a-zA-Z0-9]*","", word) # start with punc
            word = re.sub("[^a-zA-Z0-9]*$","", word) # end with punc
        
        if len(word) < 2:  # filter out 1-length word
            continue
        if word in stopwordHash:  # filter out stopwords
            continue        
        validWordNum += 1

        ### option2: no stem
        if engDetector.check(word) is True: #current word is an English word
            newArr.append(word)
            if englishDetectDebug:
                print "Eng#"+word,
        else:
            nonEngNum += 1
            if englishDetectDebug:
                print "Non-Eng#" + word,
            continue
    
    if (validWordNum > 0) & (nonEngNum > 0) & (nonEngNum > (0.8*validWordNum)): # more than 0.8 nonEngword of all validwords --> non-Eng tweet
        if englishDetectDebug:
            print ""
            print "-Final output: Non-Eng tweet - " + str(nonEngNum) + " / " + str(validWordNum) + " = " + str(nonEngNum*1.0/validWordNum)
        return ""
    if englishDetectDebug:
        print ""
        print "-Final output:" + " ".join(newArr) + " - ",
        if (validWordNum > 0) & (nonEngNum > 0):
            print str(nonEngNum) + " / " + str(validWordNum) + " = " + str(nonEngNum*1.0/validWordNum)
        else:
            print "0/0"
    
    return " ".join(newArr)

'''        ### option1: stem english word
        if engDetector.check(word) is True: #current word is an English word
            # stem each countable word except contains hashtag
            stemWord = stemmer.stem(word)
            newArr.append(stemWord)
            if englishDetectDebug:
                print "Eng#"+stemWord,            
            if stemWord in stemWordHash:
                oriWordHash = stemWordHash[stemWord]
                if word in oriWordHash:
                    oriWordHash[word] += 1
                else:
                    oriWordHash[word] = 1
                stemWordHash[stemWord] = oriWordHash                
            else:
                oriWordHash = {}
                oriWordHash[word] = 1
                stemWordHash[stemWord] = oriWordHash
        else:
            nonEngNum += 1
            if englishDetectDebug:
                print "Non-Eng#" + word,
            continue
'''


########################################################
## the main Function
currDir = os.getcwd()
stopwordsFilePath = currDir + "/.." + r"/tools/stoplist.dft"
#dirPath = currDir + "/.." + r"/Data/allData_files"
#dirPath = currDir + "/.." + r"/Data/Jan"
#dirPath = currDir + "/.." + r"/Data/20110123"
#dirPath = currDir + "/.." + r"/Data/20110123000"
#dirPath = currDir + "/.." + r"/Data/bug-fixing"
dirPath = currDir + "/../.." + r"/twitter_NUS/201301_files"
#dirPath = currDir + "/.." + r"/Data/20130103"

outputDirPath = currDir + "/.." + r"/output/"+ os.path.basename(dirPath) + r"_preprocess/"
if not os.path.exists(outputDirPath):
    os.makedirs(outputDirPath)
global inputDir_startTime
startTime = time.strftime("%Y-%m-%d_%H-%M", time.localtime())
inputDir_startTime = os.path.basename(dirPath) + "_" + startTime

print "Program starts at time:" + str(time.asctime())

loadStopword(stopwordsFilePath)
loadDataFromFiles(dirPath, outputDirPath)

print "Attributes lost:" + str(lackAttHash.keys())
print "***All lines in file: " + str(lineStringNumber)
print "Illegal JsonFormat Tweet Number: " + str(illegalJsonFormatNumber)
print "Null Tweet ID Tweet number: " + str(nullIDTweetsNumber)
print "Null user ID String number: " + str(nullUIDTweetsNumber)
print "***Null Eng-content Tweet number: " + str(lineStringNumber-legalTweetsNumber-illegalJsonFormatNumber-nullIDTweetsNumber-nullUIDTweetsNumber-nullRTTweetsNumber)
print "***Legal Tweet number: " + str(legalTweetsNumber)
print "***User number: " + str(len(userHash))
print "***Word number: " + str(len(wordHash))
rtWordNum = 0
hashWordNum = 0
for word in wordHash:
    if word.find("@") == 0:
        rtWordNum += 1
    if word.find("#") == 0:
        hashWordNum += 1
print "***RT usr word: " + str(rtWordNum)
print "***Hash tagged word: " + str(hashWordNum)

print "***Tweet length distribution: " + str(len(tweetLengHash)) + " kind of length"
sortedTweLenList = sorted(tweetLengHash.items(), key = lambda a:a[1], reverse = True)
print sortedTweLenList
sumLen = 0.0
for key in sortedTweLenList:
    sumLen += key[0]*key[1]
print "***Average tweet length: " + str(sumLen/legalTweetsNumber)

print "Program ends at time:" + str(time.asctime())
