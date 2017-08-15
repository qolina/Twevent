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

def tobinary(num, length):
    bnum = bin(num)
    bStr = bnum[2:]
    if len(bStr) > length: 
        print "Error length > feature num " + str(length) + " " + str(num) + " bStr " + bStr + " " + bnum
        return -1
    if len(bStr) < length:
        bStr = bStr.zfill(length)
    return bStr

def assignWeight(eventVecHash):
    for fea in eventVecHash:
        feaId = int(fea[0:2])
        if feaId in positiveSet:
            eventVecHash[fea] = 1 - eventVecHash[fea]
    return eventVecHash

def loadData(dirPath, featureFileHead, labelFileHead):
    global featureHash, labelHash, hashtagNum, prefixNum, suffixNum
    hashtagNum = 0
    prefixNum = 0
    suffixNum = 0
    fileList = os.listdir(dirPath)
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
            print "### Loading ends. " + str(time.asctime()) + " " + str(len(labelHash)) + " events' label are loaded from " + item 
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
                    eventVecHash = assignWeight(eventVecHash)
                    
                    if lexiconFeature:
                        if hashtagNum*prefixNum*suffixNum == 0:
                            hashtagNum = len(eventVecHash["14ftg"])
                            prefixNum = len(eventVecHash["15prf"])
                            suffixNum = len(eventVecHash["16sfx"])
                    ## filter out some features
                    if not lexiconFeature:
                        print [[fea,eventVecHash[fea]] for fea in featureSet] 
                    else:
                        print [[fea,eventVecHash[fea]] for fea in featureSet[0:14]] 
                    if toDeleteID != -1:
                        del eventVecHash[featureSet[featureMap[toDeleteID]]]
                    featureHash[day_eventID] = eventVecHash
    #                print day_eventID + eventStr
                except EOFError:
                    print "### Loading ends. " + str(time.asctime()) + " " + str(len(featureHash)) + " events' feature vector are loaded from " + item 
                    break
            featureFile.close()

def outputToFile(outputDirPath):
    outDataFile = file(outputDirPath + r"EventDataset" + outputSuffix, "w")
    fileList = [outDataFile]
    if outputTDTset:
        outTrainDataFile = file(outputDirPath + r"EventTrainDataset" + outputSuffix, "w")
        outDevDataFile = file(outputDirPath + r"EventDevDataset" + outputSuffix, "w")
        outTestDataFile = file(outputDirPath + r"EventTestDataset" + outputSuffix, "w")
        fileList = [outDataFile, outTrainDataFile, outDevDataFile, outTestDataFile]
    clusterHourHash = {}

    ## write declare into arf format outputDataFile
    if not libsvmFormat:
        outDataFile.write("@relation whole_event_cluster_feature" + outputSuffix + "\n\n")
        if outputTDTset:
            outTrainDataFile.write("@relation train_event_cluster_feature" + outputSuffix + "\n\n")
            outDevDataFile.write("@relation dev_event_cluster_feature" + outputSuffix + "\n\n")
            outTestDataFile.write("@relation test_event_cluster_feature" + outputSuffix + "\n\n")
        if lexiconFeature:
            print "hashtag_Num prefix_Num suffix_Num: " + str(hashtagNum) + " " + str(prefixNum) + " " + str(suffixNum)
        for outFile in fileList:
            attid = 0
            for fea in subFeatureSet:
                feaID = int(fea[0:2])
                if (feaID!=14)&(feaID!=15)&(feaID!=16):
                    outFile.write("@attribute " + str(feaID) + " numeric\n")
                    attid = feaID + 1
                else:
                    if lexiconFeature:
                        for i in range(attid, attid + hashtagNum):
                            outFile.write("@attribute " + str(i) + " {0, 1}\n")
                        attid += hashtagNum
                    else:
                        outFile.write("@attribute " + str(feaID) + " numeric\n")
                        attid = feaID + 1
            outFile.write("@attribute class {T, F}\n\n@data\n")

    ## write data into outputDataFile
    eNum = 0
    for item in sorted(featureHash.items(), key = lambda a:a[0]):
        label = labelHash[item[0]]
        eVechash = featureHash[item[0]]
        ftgHash = {}
        prfHash = {}
        sfxHash = {}
        if lexiconFeature:
            if "14ftg" in eVechash:
                ftgHash = eVechash["14ftg"]
                del eVechash["14ftg"]
            if "15prf" in eVechash:
                prfHash = eVechash["15prf"]
                del eVechash["15prf"]
            if "16sfx" in eVechash:
                sfxHash = eVechash["16sfx"]
                del eVechash["16sfx"]
        # output basic Features
        featureVector = list([pair[1] for pair in sorted(eVechash.items(), key = lambda a:a[0])])
        outputStr_libsvm = classHash[label]
        outputStr_arff = ""
        libFeaID = 1
        for value in featureVector:
            outputStr_arff += str(value) + ","
            outputStr_libsvm += " " + str(libFeaID)+":"+str(value)
            libFeaID += 1

        # output text Feature 
        ftgStr = ""
        prfStr = ""
        sfxStr = ""
        if lexiconFeature:
            if len(ftgHash) > 0:
         #       print "freq hashtag: " + str(len(ftgHash))  + " " + str(sum(ftgHash.values()))
                feaList= list([str(val) for val in ftgHash.values()])
                libFeaList = list([str(libFeaID+i)+":"+feaList[i] for i in range(hashtagNum)])
                libFeaID += hashtagNum
                if libsvmFormat:
                    ftgStr = " " + " ".join(libFeaList)
                else:
                    ftgStr = ",".join(feaList) + ","
            if len(prfHash) > 0:
         #       print "freq hashtag prefix: " + str(len(prfHash))  + " " + str(sum(prfHash.values()))
                feaList= list([str(val) for val in prfHash.values()])
                libFeaList = list([str(libFeaID+i)+":"+feaList[i] for i in range(prefixNum)])
                libFeaID += prefixNum
                if libsvmFormat:
                    prfStr = " " + " ".join(libFeaList)
                else:
                    prfStr = ",".join(feaList) + ","
            if len(sfxHash) > 0:
         #       print "freq hashtag suffix: " + str(len(sfxHash))  + " " + str(sum(sfxHash.values()))
                feaList= list([str(val) for val in sfxHash.values()])
                libFeaList = list([str(libFeaID+i)+":"+feaList[i] for i in range(suffixNum)])
                libFeaID += suffixNum
                if libsvmFormat:
                    sfxStr = " " + " ".join(libFeaList)
                else:
                    sfxStr = ",".join(feaList[0:suffixNum]) + ","
        outputStr_arff += ftgStr + prfStr + sfxStr
        outputStr_arff += classHash[label]
        outputStr_libsvm += ftgStr + prfStr + sfxStr

        if libsvmFormat:
            outDataFile.write(outputStr_libsvm + "\n")
        else:
            outDataFile.write(outputStr_arff + "\n")
        if outputTDTset:
            if item[0][0:2] in devSet:
                if libsvmFormat:
                    outDevDataFile.write(outputStr_libsvm + "\n")
                else:
                    outDevDataFile.write(outputStr_arff + "\n")
            elif item[0][0:2] in testSet:
                if libsvmFormat:
                    outTestDataFile.write(outputStr_libsvm + "\n")
                else:
                    outTestDataFile.write(outputStr_arff + "\n")
            else:
                if libsvmFormat:
                    outTrainDataFile.write(outputStr_libsvm + "\n")
                else:
                    outTrainDataFile.write(outputStr_arff + "\n")

        eNum += 1
        day = item[0][0:item[0].find("_")]
        if day in clusterHourHash:
            clusterHourHash[day] += 1
        else:
            clusterHourHash[day] = 1
    for outFile in fileList:
        outFile.close()
    print "### Writing ends. " + str(eNum) + " events' feature vector are writen to " + outDataFile.name
    if outputTDTset:
        print "### Writing ends. TrainFile, devFile and testFile are writen to " + outputDirPath
#    print "###ClusterNum in Days: " + str(clusterHourHash)

def getParameters(args):
    outputSuffix = ""
    toDeleteID = -1
    libsvmFormat = True
    lexiconFeature = False
    outputTDTset = False
    if len(args) == 1:
        print "Usage: python arfFormatData.py [options]"
        print "-vs vecfilesuffix -s1 fileSuffix1 -s2 fileSuffix2 -t toDeletefeaId -b useBinaryFeature -p positiveNum -lex -tdt -arff"
        sys.exit()
    if "-s1" in args:
        outputSuffix += "_" + args[args.index("-s1") + 1]
    if "-vs" in sys.argv:
        suffixStr = "_" + args[args.index("-vs")+1]
        outputSuffix += suffixStr
    else:
        if lexiconFeature:
            suffixStr += "_lexicon"
        else:
            suffixStr += "_normal"
        if "11dup" in featureSet:
            suffixStr += "_with11dup"
        else:
            suffixStr += "_no11dup"
    if "-s2" in args:
        outputSuffix += "_" + args[args.index("-s2") + 1]
    if "-t" in args:
        toDeleteID = int(args[args.index("-t") + 1])
    if "-p" in args:
        pnum = args[args.index("-p")+1]
        outputSuffix += "_" + pnum
        pSignal = tobinary(int(pnum), len(featureSet)-3)
        positiveSet = []
        for i in range(1, len(featureSet)-2):
            if pSignal[i-1] == "1":
                if "11dup" in featureSet:
                    positiveSet.append(i)
                else:
                    if (i == 11) | (i == 12):
                        positiveSet.append(i+1)
                    else:
                        positiveSet.append(i)

    else:
#        positiveSet = manualPositiveSet
        positiveSet = []
    if "-arff" in args:
        outputSuffix += ".arff"
        libsvmFormat = False
    else:
        outputSuffix += ".libsvm"
    if "-lex" in args:
        lexiconFeature = True
    if "-tdt" in args:
        outputTDTset = True
    return toDeleteID, libsvmFormat, suffixStr, outputSuffix, positiveSet, lexiconFeature, outputTDTset 

###################################################
### main function
print "###Data formatting program starts at time:" + str(time.asctime())
global featureSet, manualPositiveSet, featureMap, classHash, devSet, testSet
global outputSuffix, toDeleteID, libsvmFormat, positiveSet
global lexiconFeature, outputTDTset 

#v1: "11fav" --> not useful
#v2: no "11???" 
#v3: "11dup" --> duplication of stemmed segments 
#featureSet = ["01mue", "02seg", "03edg", "04sve", "05dfe", "06udf", "07rtm", "08men", "09rep", "10url", "12tag", "13pst", "14ftg", "15prf", "16sfx"]
#featureSet = ["01mue", "02seg", "03edg", "04sve", "05dfe", "06udf", "07rtm", "08men", "09rep", "10url", "11fav", "12tag", "13pst", "14ftg", "15prf", "16sfx"]
featureSet = ["01mue", "02seg", "03edg", "04sve", "05dfe", "06udf", "07rtm", "08men", "09rep", "10url", "11dup", "12tag", "13pst", "14ftg", "15prf", "16sfx", "17sim"]
# according to manual centroids
if "11dup" in featureSet:
    #manualPositiveSet= [1, 2, 6, 9, 11, 12]
    #manualPositiveSet= [5, 6, 7, 10, 11, 12, 13]#mpos1
#    manualPositiveSet= [1, 2, 3, 4, 8, 10, 12, 13] #mpos2
    manualPositiveSet= [1, 2, 3, 4, 8, 10, 12, 13, 17] #mpos2Temp
else:
    manualPositiveSet= [1, 2, 6, 9, 10, 12]
featureMap = {}
for feaNum in range(0, len(featureSet)):
    fea = featureSet[feaNum]
    feaid = int(fea[0:2])
    featureMap[feaid] = feaNum
classHash = {} # label:classIDStr
classHash["T"] = "1"
classHash["F"] = "0"
classHash["O"] = "0"
devSet = ["02","05"]
testSet = ["03","06","08"]
print "###Development set" + str(devSet)
print "###Test set" + str(testSet)

## get parameters from command
##python arfFormatData.py -t -1 -s1 All -s2 $suffix -b $sign -r $i -l libsvm -p pnum -lex -tdt
args = sys.argv
[toDeleteID, libsvmFormat, vecSuffixStr, outputSuffix, positiveSet, lexiconFeature, outputTDTset] = getParameters(args)
print "###Positive set" + str(positiveSet)

labelHash = {}
featureHash = {}
dirPath = r"../Data_hfmon/segged_ltwe/classify/"
featureFileHead = "EventVectorFile"
labelFileHead = "l_EventFile_"
featureFileHead += vecSuffixStr
loadData(dirPath, featureFileHead, labelFileHead)
subFeatureSet = sorted(featureHash.values()[0].keys())
print "###Feature set used: " + str(subFeatureSet)
#outputDirPath = dirPath + r"positive/"
outputDirPath = dirPath
outputToFile(outputDirPath)

print "###Program ends at time:" + str(time.asctime())

