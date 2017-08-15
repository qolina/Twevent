#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import math
import cPickle

############################
## load tweets' social feature
def loadsocialfeature(filepath):
    inFile = file(filepath,"r")
    tweSFHash = cPickle.load(inFile)
    inFile.close()
    print "### " + str(time.asctime()) + " " + str(len(tweSFHash)) + "  tweets' social features are loaded from " + inFile.name
    return tweSFHash 
'''
    feahash["RT"] = RT
    feahash["Men"] = Men
    feahash["Reply"] = Reply
    feahash["Url"] = Url
    feahash["RTC"] = RTC
    feahash["Fav"] = Fav
    feahash["Tag"] = Tag
    feahash["Past"] = Past
'''

############################
## 
def statisticHashtag(dataFilePath, toolDirPath):
    fileList = os.listdir(dataFilePath)
    # output hashtag statistics
    hashtagfreqFile = file(toolDirPath + "hashTagFreqFile", "w")
    hashtagFile = file(toolDirPath + "hashTagFile", "w")
    hashtagByTFFile = file(toolDirPath + "hashTagTFFile", "w")
    hashtagByDFFile = file(toolDirPath + "hashTagDFFile", "w")
    hashTagHashAppHash = {}
    tweetTagHash = {}
    for item in sorted(fileList):
        if item.find("segged") != 0:
            continue
        tStr = item[len(item)-2:len(item)]
        print "Time window: " + tStr

        tweetSocialFeatureFilePath = toolDirPath + "tweetSocialFeature" + tStr
        tweSFHash = loadsocialfeature(tweetSocialFeatureFilePath)
        tagHash = dict([(tid, tweSFHash[tid]["Tag"]) for tid in tweSFHash if len(tweSFHash[tid]["Tag"]) > 1])
        tweetTagHash.update(tagHash)
        print "### " + str(time.asctime()) + " " + str(len(tagHash)) + " tweets contain hashtags"
        tweSFHash.clear()
        for tid in tagHash:
            tagStr = tagHash[tid]
            tagArr = tagStr.split(" ")
            for tag in tagArr:
                illegelLetter = False
                for letter in tag:
                    encodeNum = ord(letter)
                    if (encodeNum < 32) | (encodeNum > 126):
                        illegelLetter = True
                        break
#                    if re.match("[a-zA-Z0-9]", letter):
#                        puncOnly = False
                if illegelLetter: #contain illegel letter
                    continue
                apphash = {}
                if tag in hashTagHashAppHash:
                    apphash = hashTagHashAppHash[tag]
                if tid in apphash:
                    apphash[tid] += 1
                else:
                    apphash[tid] = 1
                hashTagHashAppHash[tag] = apphash
#                print tag + " " + str(apphash)
        print "### " + str(len(hashTagHashAppHash)) + " hashtags are loaded already."

    print "### " + str(time.asctime()) + " " + str(len(hashTagHashAppHash)) + " hashtag are loaded."
    print "### " + str(time.asctime()) + " " + str(len(tweetTagHash)) + " tweets contain hashtags."
    cPickle.dump(hashTagHashAppHash, hashtagfreqFile)

    hashtagList = hashTagHashAppHash.keys()
    sortedByTF = {}
    sortedByDF = {}
    tagLenHash = {}
    for tag in sorted(hashtagList):
        apphash = hashTagHashAppHash[tag]
        df = len(apphash)
        tf = sum(apphash.values())
        sortedByTF[tag] = tf
        sortedByDF[tag] = df
        hashtagFile.write(tag + "\t" + str(tf) + "\t" + str(df) + "\n")
        tagLen = len(tag)
        if tagLen in tagLenHash:
            tagLenHash[tagLen] += 1
    else:
        tagLenHash[tagLen] = 1
    print "### " + str(sum(tagLenHash.values())) + " hash tags, length distribution: "
    print sorted(tagLenHash.items(), key = lambda a:a[1], reverse = True)

    for tagItem in sorted(sortedByTF.items(), key = lambda a:a[1], reverse = True):
        tag = tagItem[0]
        tf = tagItem[1]
        df = sortedByDF[tag]
        hashtagByTFFile.write(tag + "\t" + str(tf) + "\t" + str(df) + "\n")

    for tagItem in sorted(sortedByDF.items(), key = lambda a:a[1], reverse = True):
        tag = tagItem[0]
        df = tagItem[1]
        tf = sortedByTF[tag]
        hashtagByDFFile.write(tag + "\t" + str(tf) + "\t" + str(df) + "\n")

    hashtagFile.close()
    hashtagByTFFile.close()
    hashtagByDFFile.close()
    hashtagfreqFile.close()
    print "### " + str(time.asctime()) + " hashtag statistics (alpha order) are stored into " + hashtagFile.name
    print "### " + str(time.asctime()) + " hashtag statistics (tf) are stored into " + hashtagByTFFile.name
    print "### " + str(time.asctime()) + " hashtag statistics (df) are stored into " + hashtagByDFFile.name
    print "### " + str(time.asctime()) + " hashtag statistics (dump) are stored into " + hashtagfreqFile.name

############################
## main Function
print "###program starts at " + str(time.asctime())
dataFilePath = r"../Data_hfmon/segged_ltwe/"
toolDirPath = r"../Tools/"

statisticHashtag(dataFilePath, toolDirPath)
print "###program ends at " + str(time.asctime())
