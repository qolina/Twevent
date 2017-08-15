#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import math
import cPickle

############################
## load tweetID-usrID
def loadUsrId(filepath):
    usrFile = file(filepath,"r")
    tweIdToUsrIdHash = cPickle.load(usrFile)
    usrFile.close()
    print "loading ends " + usrFile.name
    return tweIdToUsrIdHash

############################
## getEventSegment
def statistic(dataFilePath, toolDirPath):
    fileList = os.listdir(dataFilePath)
    usrHash = {}
    for item in sorted(fileList):
        if item.find("segged") != 0:
            continue
        tStr = item[len(item)-2:len(item)]
        print "Time window: " + tStr
        tweToUsrFilePath = toolDirPath + "tweIdToUsrId" + tStr
        tweIdToUsrIdHash = loadUsrId(tweToUsrFilePath)
        usr_tHash = dict([(uid, 1) for uid in tweIdToUsrIdHash.values()])
        usrHash.update(usr_tHash)
        print "#Total num of users in time window: " + str(len(usr_tHash)) + " all users: " + str(len(usrHash))
    print "#Total num of users: " + str(len(usrHash))

############################
## main Function
global useSegmentFlag, UNIT
print "###program starts at " + str(time.asctime())
dataFilePath = r"../Data_hfmon/segged_ltwe/"
toolDirPath = r"../Tools/"
statistic(dataFilePath, toolDirPath)
print "###program ends at " + str(time.asctime())
