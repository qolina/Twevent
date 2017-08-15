#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import math
import cPickle

############################
def getHashtags(dataFilePath, outputDirPath):
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        if item.find("tweetContentFile") != 0:
            continue
        print "### Processing " + item
        tweetFile = file(dataFilePath + item)
        tStr = item[len(item)-2:len(item)]
        print "Time window: " + tStr
        hashtagFile = file(outputDirPath + "hashtagContentFile_jan" + tStr, "w")
        N_t = 0
        containHashtagNum = 0
        while True:
            lineStr = tweetFile.readline()
            lineStr = re.sub(r'\n', " ", lineStr)
            lineStr = lineStr.strip()
            if len(lineStr) <= 0:
                break
            N_t += 1
            contentArr = lineStr.split(" ")
            tweetIDstr = contentArr[0]
            hashtagStr = ""
            for word in contentArr:
                if len(word) < 1:
                    continue
                if word.find("#") >= 0:
                    hashtag = word[word.find("#"):len(word)]
#                    print "Oriword:" + word + "\thashtag:" + hashtag
                    hashtagStr += hashtag + " "
            if len(hashtagStr) < 1:
                continue
#            print lineStr
            hashtagFile.write(tweetIDstr + "\t" + hashtagStr[:-1] + "\n")
            containHashtagNum += 1

            if N_t % 100000 == 0:
                print "### " + str(time.asctime()) + " " + str(N_t) + " tweets are processed!"

        tweetFile.close()
        hashtagFile.close()
        print "### " + str(time.asctime()) + " " + str(containHashtagNum) + " tweets contain hashtag. writen to " + hashtagFile.name


############################
## main Function
print "###program starts at " + str(time.asctime())
dataFilePath = r"../Data_hfmon/"
outputDirPath = dataFilePath + "segged_ltwe_hash/"
getHashtags(dataFilePath, outputDirPath)

print "###program ends at " + str(time.asctime())
