#! /usr/bin/env python
#coding=utf-8
# evaluation of twevent
import os
import time
import math
import numpy as np

def inHash(num, testHash):
    if num in testHash:
        testHash[num] += 1
    else:
        testHash[num] = 1
    return testHash

def addHash(index, testHash):
    addedVal = 0
    if index-1 in testHash:
        addedVal = testHash[index-1]
    if index in testHash:
        testHash[index] += addedVal
    else:
        testHash[index] = addedVal
    return testHash

#dirPath = r"/home/lavender1c/yxqin/twevent/Data_hfmon/segged_qtwe/segTwe/labelledEvents/"
#dirPath = r"/home/lavender1c/yxqin/twevent/Data_hfmon/segged_ltwe/wordTwe/labelledEvents/"
#dirPath = r"/home/lavender1c/yxqin/twevent/Data_hfmon/segged_ltwe/segTwe/labelledEvents/"
dirPath = r"/home/lavender1c/yxqin/twevent/Data_hfmon/segged_ltwe_hash/segTwe/labelledEvents/"
trueEventFile = file(dirPath + r"l_trueEventList")
print "### " + str(time.asctime()) + " # Loading labelled true event file: " + trueEventFile.name
distNumHash = {}
dumpNumHash = {}
trueNumHash = {}

ratioEventHash = {}

lineArr = trueEventFile.readlines()
for lineStr in lineArr:
    if lineStr.find("###") > 0:
        arr = lineStr.split("###")
        eventId = arr[0]
#        print lineStr
        ratioIdxS = lineStr.find("ratio:") + 7
        ratioIdxE = lineStr.find(" ", ratioIdxS)
        ratioInt = int(math.ceil(float(lineStr[ratioIdxS:ratioIdxE])))
#        print "ratio: " + str(ratioInt)
        trueNumHash = inHash(ratioInt, trueNumHash)
        if ratioInt in ratioEventHash:
            trueEventHash = ratioEventHash[ratioInt]
            if eventId in trueEventHash:
                trueEventHash[eventId] += 1
            else:
                trueEventHash[eventId] = 1
            ratioEventHash[ratioInt] = trueEventHash 
        else:
            trueEventHash = {}
            trueEventHash[eventId] = 1
            ratioEventHash[ratioInt] = trueEventHash 

for i in range(2,3):
    trueNumHash = addHash(i, trueNumHash)
    trueEventHash = ratioEventHash[i]
    formerTEHash = ratioEventHash[i-1]
    for eid in formerTEHash:
        if eid in trueEventHash:
            trueEventHash[eid] += formerTEHash[eid]
        else: 
            trueEventHash[eid] = formerTEHash[eid]
    ratioEventHash[i] = trueEventHash

    distNum = len(trueEventHash)
    dumpNum = 0
    for eventId in trueEventHash:
        if trueEventHash[eventId] > 1:
            dumpNum += 1
    distNumHash[i] = distNum
    dumpNumHash[i] = dumpNum*100.0/trueNumHash[i]
dumpNumHash = dict([(ratio, round(dumpNumHash[ratio],2)) for ratio in dumpNumHash])
print "***************Recall"
print "true event num: " + str(trueNumHash)
print "distinct event num: " + str(distNumHash)
print "dumpRatio: " + str(dumpNumHash)

