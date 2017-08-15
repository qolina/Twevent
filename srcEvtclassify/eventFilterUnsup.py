#! /usr/bin/env python
# -*- coding: utf-8 -*-
#Location: D:\TweetyBird_Lab\src\arfFormatData.py
#author: qolina
#Function: data formatting for weka
#version: V1

import os
import re
import time
import cPickle
import sys
import math

def filling(string, num):
    str1 = string[0:string.find("_")]
    str2 = string[string.find("_")+1:len(string)]
    str2New = str2.zfill(3)
    return str1 + "_" + str2New

### main function
#print "Program starts at time:" + str(time.asctime())
args = sys.argv
outputStrExtra = ""
toDeleteID = -1
toDeleteID = int(args[1])
outputStrExtra = "_" + args[2] + "_" + args[3]
filterRatio = float(args[3])/100
print "Ratio: " + str(filterRatio)

#featureSet = ["01mue", "02seg", "03edg", "04sve", "05dfe", "06udf", "07rtm", "08men", "09rep", "10url", "11fav", "12tag", "13pst", "14ftg", "15prf", "16sfx"]
featureSet = ["01mue", "02seg", "03edg", "04sve", "05dfe", "06udf", "07rtm", "08men", "09rep", "10url", "12tag", "13pst", "14ftg", "15prf", "16sfx"]
featureWeight = {}
featureMap = {}
for feaNum in range(0, len(featureSet)):
    fea = featureSet[feaNum]
    feaid = int(fea[0:2])
    featureMap[feaid] = feaNum
    featureWeight[feaid] = 1.0
if int(args[4]) in featureWeight:
    featureWeight[int(args[4])] = -0.5
    print "Weak: " + args[4]

classHash = {} # label:classIDStr
classHash["T"] = 1
classHash["F"] = 0
classHash["O"] = 0

devSet = ["02","05"]
testSet = ["03","05","08"]

dirPath = r"../Data_hfmon/segged_ltwe/classify/"
featureFileHead = "EventVectorFile"
labelFileHead = "l_EventFile_"
#outDevResultFile = file(dirPath + r"filterResult_Dev_" + outputStrExtra + ".txt", "w")
fileList = os.listdir(dirPath)

labelHash = {}
featureHash = {}
for item in fileList:
    if item.startswith(labelFileHead):
        labeledFile = file(dirPath + item)
        while True:
            lineStr = labeledFile.readline()
            lineStr = re.sub(r'\n', "", lineStr)
            if len(lineStr) <= 0:
                break
            if lineStr.find("###") == 1:
                #T###Event 01_1
                day_eventID = lineStr[lineStr.find("Event ")+6:lineStr.find(" ratio:")]
                day_eventID = day_eventID.strip()
                day_eventID = filling(day_eventID, 3)
                labelHash[day_eventID] = lineStr[0]
#                print lineStr[0] + " " + day_eventID 
#        print sorted(labelHash.keys())
#        print str(len(labelHash)) + " events' label info loaded from " + item
        labeledFile.close()
    elif item.startswith(featureFileHead):
        featureFile = file(dirPath + item)
        while True:
            try:
                eventStr = cPickle.load(featureFile)
                arr = eventStr.split(" ")
                day_eventID = arr[1]
                day_eventID = day_eventID.strip()
                day_eventID = filling(day_eventID, 3)
                eventVecHash = cPickle.load(featureFile)
                eventVecHash["01mue"] = 1.0/eventVecHash["01mue"]
                ## filter out some features
                if toDeleteID != -1:
                    del eventVecHash[featureSet[featureMap[toDeleteID]]]
                featureHash[day_eventID] = eventVecHash
#                print day_eventID + eventStr
            except EOFError:
#                print str(time.asctime()) + " Feature file loading ends. Event num: " + str(len(featureHash))
                break

        featureFile.close()

subFeatureSet = sorted(featureHash.values()[0].keys())
#print "Feature set used: " + str(subFeatureSet)
eNum = 0
trainTrueEvtNum = 0
devTrueEvtNum = 0
testTrueEvtNum = 0
trainevtNum = 0
devevtNum = 0
testevtNum = 0
traintEvtNum = 0
devtEvtNum = 0
testtEvtNum = 0

labelDistri = {}
for item in sorted(featureHash.items(), key = lambda a:a[0]):
    score = 0.0
    outputStr = ""
    label = classHash[labelHash[item[0]]]
    eVechash = featureHash[item[0]]
#  unsup method 1    
#    featureVector = list([pair[1] for pair in sorted(eVechash.items(), key = lambda a:a[0])])
#    for value in featureVector:
#        score += math.pow(value,2)
#    score = math.sqrt(score)
    
#  unsup method 2    
    featureVector = list([pair[1]*featureWeight[int(pair[0][0:2])] for pair in sorted(eVechash.items(), key = lambda a:a[0])])
    score = sum(featureVector)/len(featureVector)
    score = round(score, 4)
    # statistic distribution of score
    tScore = round(score,1)
    lhash = {}
    if tScore in labelDistri:
        lhash = labelDistri[tScore]
    if label in lhash:
        lhash[label] += 1
    else:
        lhash[label] = 1
    labelDistri[tScore] = lhash

    if item[0][0:2] in devSet:
#        print "Dev Event: " + item[0] + " (" + labelHash[item[0]] + ") Score: " + str(score) + "\t"
        
        if label == 1:
            devTrueEvtNum += 1
        if score > filterRatio:
            devevtNum += 1
            if label == 1:
                devtEvtNum += 1
    elif item[0][0:2] in testSet:
        if label == 1:
            testTrueEvtNum += 1
        if score > filterRatio:
            testevtNum += 1
            if label == 1:
                testtEvtNum += 1
    else:
        if label == 1:
            trainTrueEvtNum += 1
        if score > filterRatio:
            trainevtNum += 1
            if label == 1:
                traintEvtNum += 1
    eNum += 1
print "development set" + str(devSet) + "\t",
if devevtNum > 0:
    P = round(devtEvtNum*100.0/devevtNum,2)
    R = round(devtEvtNum*100.0/devTrueEvtNum,2)
    if P+R == 0.0:
        F1 = 0.0
    else:    
        F1 = round(2*P*R/(P+R),2)
#    print "Filtered True: " + str(devtEvtNum) + ", All True: " + str(devTrueEvtNum) + ", All: " + str(devevtNum)
    print "P: " + str(P) + " R: " + str(R) + " F1: " + str(F1)
print "test set" + str(testSet) + "\t",
if testevtNum > 0:
    P = round(testtEvtNum*100.0/testevtNum,2)
    R = round(testtEvtNum*100.0/testTrueEvtNum,2)
    if P+R == 0.0:
        F1 = 0.0
    else:    
        F1 = round(2*P*R/(P+R),2)
#    print "Filtered True: " + str(testtEvtNum) + ", All True: " + str(testTrueEvtNum) + ", All: " + str(testevtNum)
    print "P: " + str(P) + " R: " + str(R) + " F1: " + str(F1)

if False:    
    for tScore in sorted(labelDistri.keys()):
        lhash = labelDistri[tScore]
        print str(tScore) + "\t",
        if 0 in lhash:
            print str(lhash[0]) + "\t",
        else:
            print "0\t",
        if 1 in lhash:
            print str(lhash[1])
        else:
            print "0"
print "******************************"
