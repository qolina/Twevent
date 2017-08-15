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
    return tweIdToUsrIdHash

############################
## load event segments from file
def loadEvtseg(filePath):
    unitHash = {}#segment:segmentID(count from 0)

    inFile = file(filePath)
    unitID = 0
    while True:
        lineStr = inFile.readline()
        lineStr = re.sub(r'\n', ' ', lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        contentArr = lineStr.split("\t")
        unit = contentArr[2]
        unitHash[unit] = unitID
        unitID += 1
    inFile.close()
    print "### " + str(len(unitHash)) + " event " + UNIT + "s are loaded from " + inFile.name
    return unitHash

############################
## getEventSegment's df
def getEventSegmentDF(dataFilePath, toolDirPath):
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        if item.find("segged") != 0:
            continue
        print "### Processing " + item
        seggedFile = file(dataFilePath + item)
        tStr = item[len(item)-2:len(item)]
        print "Time window: " + tStr
        eventSegFilePath = dataFilePath + "event" + UNIT + tStr
        unitHash = loadEvtseg(eventSegFilePath)
        eventSegDFFile = file(dataFilePath + "event" + UNIT  + "DF" + tStr, "w")
        unitDFHash = {} # unit:dfhash
        N_t = 0
        Usr_t = 0
        usrHash = {}
        unitUsrHash = {}
        tweToUsrFilePath = toolDirPath + "tweIdToUsrId" + tStr
        tweIdToUsrIdHash = loadUsrId(tweToUsrFilePath)
        while True:
            lineStr = seggedFile.readline()
            lineStr = re.sub(r'\n', " ", lineStr)
            lineStr = lineStr.strip()
            if len(lineStr) <= 0:
                break
            contentArr = lineStr.split("\t")
            tweetIDstr = contentArr[0]
            tweetText = contentArr[2]
            usrIDstr = tweIdToUsrIdHash[tweetIDstr]
            if len(tweetText)*len(tweetIDstr) == 0:
                print "Error: empty id or text: " + tweetIDstr + "#" + tweetText
                exit
            N_t += 1
            if usrIDstr not in usrHash:
                usrHash[usrIDstr] = 1
            textArr = tweetText.split("|")
            for segment in textArr:
                wordArr = segment.split(" ")
                containslang = False

                if useSegmentFlag:
                    unit = segment
                    if unit not in unitHash:
                        continue
                    # segment df
                    df_t_hash = {}
                    if unit in unitDFHash:
                        df_t_hash = unitDFHash[unit]
                    df_t_hash[tweetIDstr] = 1
                    unitDFHash[unit] = df_t_hash

                    # segment users
                    usr_hash = {}
                    if unit in unitUsrHash:
                        usr_hash = unitUsrHash[unit]
                    usr_hash[usrIDstr] = 1
                    unitUsrHash[unit] = usr_hash
                else:
                    for word in wordArr:
                        unit = word
                        if unit not in unitHash:
                            continue
                        # word df
                        df_t_hash = {}
                        if unit in unitDFHash:
                            df_t_hash = unitDFHash[unit]
                        df_t_hash[tweetIDstr] = 1
                        unitDFHash[unit] = df_t_hash

                        # word users
                        usr_hash = {}
                        if unit in unitUsrHash:
                            usr_hash = unitUsrHash[unit]
                        usr_hash[usrIDstr] = 1
                        unitUsrHash[unit] = usr_hash
            if N_t % 100000 == 0:
                print "### " + str(time.asctime()) + " " + str(N_t) + " tweets are processed!"

        windowHash[tStr] = N_t
        Usr_t = len(usrHash)
        cPickle.dump(N_t, eventSegDFFile)
        cPickle.dump(Usr_t, eventSegDFFile)
        cPickle.dump(unitDFHash, eventSegDFFile)
        cPickle.dump(unitUsrHash, eventSegDFFile)
        for unit in unitDFHash:
            print unit + "\t" + str(len(unitDFHash[unit]))
        print "### " + str(time.asctime()) + " " + str(len(unitHash)) + " event " + UNIT + "s DF/UsrDF are calculated and writen to " + eventSegDFFile.name
        seggedFile.close()
        eventSegDFFile.close()

############################
## main Function
global useSegmentFlag, UNIT
print "###program starts at " + str(time.asctime())
#dataFilePath = r"../Data_hfmon/segged_qtwe/"
dataFilePath = r"../Data_hfmon/segged_ltwe/"
#dataFilePath = r"../Data_hfmon/segged_ltwe_hash/"
# use segment or word as unit
useSegmentFlag = True 
if useSegmentFlag:
    UNIT = "segment"
else:
    UNIT = "word"
toolDirPath = r"../Tools/"
windowHash = {} # timeSliceIdStr:tweetNum

getEventSegmentDF(dataFilePath, toolDirPath)

print "###program ends at " + str(time.asctime())
