#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import math
import cPickle

############################
def getHashtags(outputDirPath, tStr):
    hashtagTweetHash = {}
    hashtagFile = file(outputDirPath + "hashtagContentFile_jan" + tStr)
    while True:
        lineStr = hashtagFile.readline()
        lineStr = re.sub(r'\n', "", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        contentArr = lineStr.split("\t")
        tweetIDstr = contentArr[0]
        hashtagArr = contentArr[1].split(" ")
        hashtagStr = contentArr[1]
        if len(hashtagArr) > 1:
            hashtagStr = "|".join(hashtagArr)
#            print hashtagStr
        hashtagTweetHash[tweetIDstr] = hashtagStr.lower()
    hashtagFile.close()
    print "### " + str(time.asctime()) + " " + str(len(hashtagTweetHash )) + " tweets containing hashtag are loaed from " + hashtagFile.name
    return hashtagTweetHash

def getHashSegged(dataFilePath, outputDirPath):
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        if item.find("segged_tweetContentFile") != 0:
            continue
        print "### Processing " + item
        tweetFile = file(dataFilePath + item)
        tStr = item[len(item)-2:len(item)]
        print "Time window: " + tStr
        hashtagTweetHash = getHashtags(outputDirPath, tStr)
        newSeggedFile = file(outputDirPath + "segged_hash_tweetContentFile_jan" + tStr, "w")
        N_t = 0
        containHashtagNum = 0
        while True:
            lineStr = tweetFile.readline()
            lineStr = re.sub(r'\n', "", lineStr)
            lineStr = lineStr.strip()
            if len(lineStr) <= 0:
                break
            N_t += 1
            contentArr = lineStr.split("\t")
            tweetIDstr = contentArr[0]
            newSeggedStr = contentArr[2]
            if tweetIDstr in hashtagTweetHash:
                newSeggedStr += "|" + hashtagTweetHash[tweetIDstr]
                containHashtagNum += 1
#                print newSeggedStr
                newSeggedFile.write(tweetIDstr + "\t" + contentArr[1] + "\t" + newSeggedStr + "\n")
            else:
                newSeggedFile.write(lineStr + "\n")

            if N_t % 100000 == 0:
                print "### " + str(time.asctime()) + " " + str(N_t) + " tweets are processed!"

        tweetFile.close()
        newSeggedFile.close()
        print "### " + str(time.asctime()) + " " + str(containHashtagNum) + " tweets contain hashtag. new segged tweet file writen to " + newSeggedFile.name

############################
## main Function
print "###program starts at " + str(time.asctime())
dataFilePath = r"../Data_hfmon/segged_ltwe/"
outputDirPath = r"../Data_hfmon/segged_ltwe_hash/"
getHashSegged(dataFilePath, outputDirPath)

print "###program ends at " + str(time.asctime())
