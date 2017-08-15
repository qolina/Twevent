#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import cPickle

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

def readTime(timeStr):
    #Time format in tweet: "Sun Jan 23 00:00:02 +0000 2011"
    tweetTimeFormat = r"%a %b %d %X +0000 %Y"
    createTime = time.strptime(timeStr, tweetTimeFormat)
    return createTime
favNum  = 0
print "###program starts at " + str(time.asctime())
dataFilePath = r"../corpus_struct/"
outputStr = "tweetSocialFeature"
M = 12
fileList = os.listdir(dataFilePath)
for item in sorted(fileList):
    if item.find("tweetFile_") != 0:
        continue
    print "### Processing " + item
    tStr = item[len(item)-2:len(item)]
    outputFile = file(dataFilePath + outputStr  + tStr, "w")
    attriHash = {}
    tweFile = file(dataFilePath + item, "rb")
    tweetNum_t = 0
    ntlist = {}
    while True:
        try:
            currTweet = cPickle.load(tweFile)
            tweetIDstr = currTweet.id_str
            usrIDstr = currTweet.user_id_str
            timeStr = readTime(currTweet.created_at)
            hourStr = time.strftime("%H", timeStr)
            hourInterval = int(hourStr)%M
            if hourInterval in ntlist:
                ntlist[hourInterval] += 1
            else:
                ntlist[hourInterval] = 1
#            print hourStr + " " + time.strftime("%H-%M-%S", timeStr)
            RT = False
            Men = False
            Reply = False
            Url = False
            RT1 = currTweet.retweeted
            if len(currTweet.text) > 5:
                partText = currTweet.text[0:4].lower()
                if partText.startswith("rt @"): 
                    RT = True
#                    print "rt @: " + str(currTweet.text[0:5])
            if len(currTweet.user_mentions) > 0:
                Men = True
#                print "Men: " + str(Men)
            if currTweet.in_reply_to_status_id_str != None:
                Reply = True
#                print "Reply: " + str(Reply)
            if len(currTweet.urls) > 0:
                Url = True
#                print "Url: " + str(Url)
            Fav = currTweet.favorited
            if Fav:
                favNum += 1
            Tag = ""
            for tag in currTweet.hashtags:
                hashtag = "#" + tag["text"]
                Tag += hashtag + " "
            if len(Tag) > 1:
                Tag = Tag[:-1]
#                print Tag
            wordArr = currTweet.text.split(" ")
            Past = ""
            for word in wordArr:
                if word.endswith("ed"):
                    Past += word + " "
            if len(Past) > 1:
                Past = Past[:-1]
#                print Past
                
            # output into file
            feahash = {}
            feahash["Usr"] = usrIDstr
            feahash["Time"] = hourStr
            feahash["RT"] = RT
            feahash["Men"] = Men
            feahash["Reply"] = Reply
            feahash["Url"] = Url
            feahash["Fav"] = Fav
            feahash["Tag"] = Tag
            feahash["Past"] = Past
#            print feahash
            attriHash[tweetIDstr] = feahash 
            tweetNum_t += 1
            if tweetNum_t % 10000 == 0:
                print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed!"
                print "### tweet num: " + str(ntlist)
        except EOFError:
            print "### " + str(time.asctime()) + " tweets in " + item + " are loaded." + str(len(attriHash))
            tweFile.close()
            break
    cPickle.dump(attriHash, outputFile)
    print "### tweetID:" + outputStr + " in time window " + tStr + " is dumped to " + outputFile.name
    print "### tweet num: " + str(ntlist)
    print "favorited tweet num: " + str(favNum)
    outputFile.close()

print "###Favorited tweet num: " + str(favNum)
print "###program ends at " + str(time.asctime())
