#! /usr/bin/env python
#coding=utf-8
# evaluation of twevent
import os
import time
import math
import numpy as np

def loadHoroscopeWords(path):
    horoFile = file(path)
    lineArr = horoFile.readlines()
    horolist = []
    for line in lineArr:
        horolist.append(line[:-1])
    return horolist

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

def getPrecision(eNumHash, tNumHash, fNumHash, dNumHash):
    tRatioHash = {}
    fRatioHash = {}
    dRatioHash = {}
    for i in range(2,tThreshold):
        eNumHash = addHash(i, eNumHash)
        tNumHash = addHash(i, tNumHash)
        fNumHash = addHash(i, fNumHash)
        dNumHash = addHash(i, dNumHash)
        tRatioHash[i] = tNumHash[i]*100.0/eNumHash[i]
        fRatioHash[i] = fNumHash[i]*100.0/eNumHash[i]
        dRatioHash[i] = dNumHash[i]*100.0/eNumHash[i]
    return eNumHash, tRatioHash, fRatioHash, dRatioHash

def statMic(testHash, num, i):
    numList = []
    if i in testHash:
        numList = testHash[i]
    numList.append(num)
    testHash[i] = numList
    return testHash

# main function
global tThreshold, horoWordList 
tThreshold = 10
#dirPath = r"/home/lavender1c/yxqin/twevent/Data_hfmon/segged_qtwe/segTwe/labelledEvents/"
#dirPath = r"/home/lavender1c/yxqin/twevent/Data_hfmon/segged_qtwe_v1/v2_labelledEvents/"
dirPath = r"/home/lavender1c/yxqin/twevent/Data_hfmon/segged_ltwe/classify/"
#dirPath = r"/home/lavender1c/yxqin/twevent/Data_hfmon/segged_ltwe/wordTwe/labelledEvents/"
#dirPath = r"/home/lavender1c/yxqin/twevent/Data_hfmon/segged_ltwe/segTwe/labelledEvents/"
#dirPath = r"/home/lavender1c/yxqin/twevent/Data_hfmon/segged_ltwe_hash/segTwe/labelledEvents/"
toolPath = r"/home/lavender1c/yxqin/twevent/Tools/horoscopeWords"
filterHoroObvious = False #True
filterHoroAll = False
print "### " + str(time.asctime()) + " # Loading labelled files from directory: " + dirPath
horoWordList = loadHoroscopeWords(toolPath)
fileList = os.listdir(dirPath)
fileList.sort()
eventFile = file(dirPath + r"eventList", "w")
trueEventFile = file(dirPath + "trueEventList", "w")
falseEventFile = file(dirPath + "falseEventList", "w")

mac_tRatioHash = {}
mac_fRatioHash = {}
mac_dRatioHash = {}
mac_eNumHash = {}

mic_tRatioHash = {}
mic_fRatioHash = {}
mic_dRatioHash = {}
mic_eNumHash = {}

for item in fileList:
#    if not item.startswith("l_qtwe_seg_EventFile"):
#    if not item.startswith("l_ltwe_word_EventFile"):
 #   if not item.startswith("l_ltwehash_seg_EventFile"):
    if not item.startswith("l_EventFile"):
        continue
    if item.startswith("l_EventFile_k"):
        continue
    lbl_eventFile = file(dirPath + item)
    print "*********************Reading file: " + item
    eventFile.write("************************************File: " + item + "\n")
    trueEventFile.write("************************************File: " + item + "\n")
    falseEventFile.write("************************************File: " + item + "\n")
    lineArr = lbl_eventFile.readlines()
    tRatioHash = {}
    fRatioHash = {}
    dRatioHash = {}
    eNumHash = {}
    trueEventFlag = False
    falseEventFlag = False
    lineIdx = 0
    while lineIdx < len(lineArr):
        lineStr = lineArr[lineIdx]
        if lineStr.startswith("***"):
            line1 = lineArr[lineIdx + 1]
            arr = line1.split("#")
            if filterHoroObvious: # filter out obvious horoscope topic
                if arr[0] == "F0":
                    lineIdx += 6
                    continue
            if filterHoroAll: # filter out all possible horoscope topic
                if arr[0].startswith("F0"):
                    lineIdx += 6
                    continue
            segmentList = lineArr[lineIdx+4][:-1].split("||")
            wordList = []
            for segment in segmentList:
                wArr = segment.split(" ")
                wordList.extend(wArr)
            horoflag = False
            for horoWord in horoWordList:
                for word in wordList:
                    #if word.find(horoWord) == 0:
                    if word == horoWord:
                        print lineArr[lineIdx + 1][:-1]
                        print horoWord + "\t#" + str(wordList)
                        print lineArr[lineIdx + 4][:-1]
                        horoflag = True
                        break
            if horoflag:
                lineIdx += 6
                continue
            ratioIdxS = line1.find("ratio:") + 7
            ratioIdxE = line1.find(" ", ratioIdxS)
            ratioInt = int(math.ceil(float(line1[ratioIdxS:ratioIdxE])))
#            print line1
#            print "ratio: " + str(ratioInt)
            mac_eNumHashe = inHash(ratioInt, mac_eNumHash)
            eNumHash = inHash(ratioInt, eNumHash)
            eventFile.write("###" + arr[0] + "###" + arr[3])
            if len(arr[1]) > 1:
                eventFile.write("##Detail e1: " + arr[1] + "\n")
            if len(arr[2]) > 1:
                eventFile.write("##Detail e2: " + arr[2] + "\n")
            
            if arr[0].startswith("T") | arr[0].startswith("t#"):
 #               print "True: " + line1
                trueEventFile.write("###" + arr[0] + "###" + arr[3])
                if len(arr[1]) > 1:
                    trueEventFile.write("##Detail e1: " + arr[1] + "\n")
                if len(arr[2]) > 1:
                    trueEventFile.write("##Detail e2: " + arr[2] + "\n")
                trueEventFlag = True
                mac_tRatioHash = inHash(ratioInt, mac_tRatioHash)
                tRatioHash = inHash(ratioInt, tRatioHash)
            elif arr[0].startswith("F") | arr[0].startswith("f"):
 #               print "False: " + line1
                mac_fRatioHash = inHash(ratioInt, mac_fRatioHash)
                fRatioHash = inHash(ratioInt, fRatioHash)
                falseEventFlag = True
                if ratioInt <= 2:
                    falseEventFile.write("###" + arr[0] + "###" + arr[3])
                    if len(arr[1]) > 1:
                        falseEventFile.write("##Detail e1: " + arr[1] + "\n")
                    if len(arr[2]) > 1:
                        falseEventFile.write("##Detail e2: " + arr[2] + "\n")
            elif arr[0].startswith("?"):
 #               print "Multi: " + line1
                mac_dRatioHash = inHash(ratioInt, mac_dRatioHash)
                dRatioHash = inHash(ratioInt, dRatioHash)
                falseEventFlag = True
                if ratioInt <= 2:
                    falseEventFile.write("###" + arr[0] + "###" + arr[3])
                    if len(arr[1]) > 1:
                        falseEventFile.write("##Detail e1: " + arr[1] + "\n")
                    if len(arr[2]) > 1:
                        falseEventFile.write("##Detail e2: " + arr[2] + "\n")
            line4 = lineArr[lineIdx + 4]
            eventFile.write(line4)
            if trueEventFlag:
                trueEventFile.write(line4)
                trueEventFlag = False
            if falseEventFlag:
                if ratioInt <= 2:
                    falseEventFile.write(line4)
                falseEventFlag = False
        lineIdx += 6
    [eNumHash, tRatioHash, fRatioHash, dRatioHash] = getPrecision(eNumHash, tRatioHash, fRatioHash, dRatioHash)
    for i in range(2,tThreshold):
        eNum = eNumHash[i]
        tPre = tRatioHash[i]
        fPre = fRatioHash[i]
        dPre = dRatioHash[i]
        if False:
            print "##Ratio: " + str(i)
            print "Events Num: " + str(eNum)
            print "True Precision: " + str(round(tPre,2)) + "%; Precision(plus doubt) " + str(round(tPre + dPre, 2)) + "%"
            print "False Event Ratio: " + str(round(fPre, 2)) + "%"
            print "doubt Event Ratio: " + str(round(dPre, 2)) + "%\n"
        mic_eNumHash = statMic(mic_eNumHash, eNum, i)
        mic_tRatioHash = statMic(mic_tRatioHash, tPre, i)
        mic_fRatioHash = statMic(mic_fRatioHash, fPre, i)
        mic_dRatioHash = statMic(mic_dRatioHash, dPre, i)

    lbl_eventFile.close()
eventFile.close()
trueEventFile.close()
falseEventFile.close()

print "*****************************************Macro Result: "
[mac_eNumHash, mac_tRatioHash, mac_fRatioHash, mac_dRatioHash] = getPrecision(mac_eNumHash, mac_tRatioHash, mac_fRatioHash, mac_dRatioHash)
for i in range(2,tThreshold):
    eNum = mac_eNumHash[i]
    tPre = mac_tRatioHash[i]
    fPre = mac_fRatioHash[i]
    dPre = mac_dRatioHash[i]
    print "##Ratio: " + str(i)
    print "Events Num: " + str(eNum)
    print "True Precision: " + str(round(tPre,2)) + "%; Precision(plus doubt) " + str(round(tPre + dPre, 2)) + "%"
    print "False Event Ratio: " + str(round(fPre, 2)) + "%"
    print "doubt Event Ratio: " + str(round(dPre, 2)) + "%\n"

print "*****************************************Micro Result: "
for i in range(2,tThreshold):
    eNumList = mic_eNumHash[i]
    tPreList = mic_tRatioHash[i]
    fPreList = mic_fRatioHash[i]
    dPreList = mic_dRatioHash[i]
    timeWinNum = len(eNumList)
    tPre = np.mean(tPreList)
    fPre = np.mean(fPreList)
    dPre = np.mean(dPreList)
    print "##Ratio: " + str(i)
#    print "True Precision: " + str(round(tPre,2)) + "%; Precision(plus doubt) " + str(round(tPre + dPre, 2)) + "%"
#    print "False Event Ratio: " + str(round(fPre, 2)) + "%"
#    print "doubt Event Ratio: " + str(round(dPre, 2)) + "%"
    tNumList = list([int(eNumList[tw]*tPreList[tw]/100) for tw in range(0, timeWinNum)])
    tPreList = list([round(val,2) for val in tPreList])
    tPreStrList = list([str(val) for val in tPreList])
    tPreStrList1 = list([str(round(val*1.0/100,2)) for val in tPreList])
    tPreStrList2 = list([str(round(val*10.0/100,2)) for val in tPreList])
    fPreList = list([round(val,2) for val in fPreList])
    dPreList = list([round(val,2) for val in dPreList])
    print "#Event Num: " + str(eNumList)
    print "#TrueE Num: " + str(tNumList)
    print "#Precision: " + str(tPreList)
#    print "\t".join(tPreStrList)
#    print "\t".join(tPreStrList1)
#    print "\t".join(tPreStrList2)
    print "#Drecision: " + str(dPreList)
    print "#Frecision: " + str(fPreList)
    print "\n"
