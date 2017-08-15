#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import math
import cPickle

class Event:
    def __init__(self, eventId):
        self.eventId = eventId
    
    def updateEvent(self, nodeList, edgeHash):
        self.nodeList = nodeList
        self.edgeHash = edgeHash

############################
## load df from file
def loadDF(dfFilePath):
    global wordDFHash, TWEETNUM 
    windowHash = {}
    dfFile = file(dfFilePath)
    firstLine = dfFile.readline()
# Format:01 num1#02 num2#...#15 num15
    itemArr = firstLine.split("#")
    for item in itemArr:
        arr = item.split(" ")
        tStr = arr[0]
        tweetNum = int(arr[1])
        windowHash[tStr] = tweetNum
    print "### Loaded tweets Num in each time window: "
    print sorted(windowHash.items(), key = lambda a:a[0])
    TWEETNUM = sum(windowHash.values())
    while True:
        lineStr = dfFile.readline()
        lineStr = re.sub(r'\n', ' ', lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        contentArr = lineStr.split("\t")
        df = int(contentArr[0])
        word = contentArr[1]
        wordDFHash[word] = df
#        print "Word: #" + word + "# df: " + str(df)
    dfFile.close()
    print "### " + str(len(wordDFHash)) + " words' df values are loaded from " + dfFile.name

############################
## load event segments from file
def loadEvtseg(filePath):
    unitHash = {}#segment:segmentID(count from 0)
    unitDFHash = {} # segmentID:f_st

    #[GUA] eventSegFile name: eventSeg + TimeWindow, format: f_st(twitterNum / segment, timeWindow), wb_st(bursty score), segment
    inFile = file(filePath)
    unitID = 0
    while True:
        lineStr = inFile.readline()
        lineStr = re.sub(r'\n', ' ', lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        contentArr = lineStr.split("\t")
        f_st = int(contentArr[0])
        unit = contentArr[2]
        unitHash[unit] = unitID
        unitDFHash[unitID] = f_st
        unitID += 1
    inFile.close()
    print "### " + str(len(unitHash)) + " event " + UNIT + "s and f_st values are loaded from " + inFile.name

    #[GUA] segmentHash mapping: segment -> segID, segmentDFHash mapping: segID -> f_st
    return unitHash, unitDFHash

############################
## load tweetID-createdHour
def loadTime(filepath):

    #[GUA] usrHour name: tweIdToUsrId + TimeWindow, format: twitterID -> hourStr([00, 23])
    inFile = file(filepath,"r")
    timeHash = cPickle.load(inFile)
    inFile.close()
    return timeHash

############################
## calculate similarity of two segments
def calSegPairSim(segAppHash, segTextHash, unitDFHash, docNum):
    segPairHash = {}
    segfWeiHash = {}
    segTVecHash = {}
    segVecNormHash = {}
    for segId in segAppHash:

        #[GUA] m_eSegAppHash mapping: segID -> [twitterID -> 1/0]
        #[GUA] m_eSegTextHash mapping: segID -> twitterText(segment|segment|...)###twitterText###...
        #[GUA] segmentDFHash mapping: segID -> f_st
        #[GUA] segmentDFHash mapping: twitterNum
        f_st = unitDFHash[segId]
        f_stm = len(segAppHash[segId])

        #[GUA] f_st(twitterNum / segment, timeWindow), f_stm(twitterNum / segment, interval)
        f_weight = f_stm * 1.0 / f_st
        segfWeiHash[segId] = f_weight
#        print "###" + str(segId) + " fweight: " + str(f_weight),
#        print " f_stm: " + str(f_stm) + " f_st: " + str(f_st)
        segText = segTextHash[segId]
        if segText.endswith("###"):
            segText = segText[:-3]
#        print "Appeared Text: " + segText[0:50]

        #[GUA] featureHash mapping: segment -> tf-idf 
        [featureHash, norm] = toTFIDFVector(segText, docNum)
        segTVecHash[segId] = featureHash
        segVecNormHash[segId] = norm
#        print "###" + str(segId) + " featureNum: " + str(len(featureHash)),
#        print " norm: " + str(norm)
#        print featureHash

    # calculate similarity
    segList = sorted(segfWeiHash.keys())
    segNum = len(segList)
    for i in range(0,segNum):
        for j in range(i+1,segNum):
            segId1 = segList[i]
            segId2 = segList[j]
            segPair = str(segId1) + "|" + str(segId2)
            tSim = textSim(segTVecHash[segId1], segVecNormHash[segId1], segTVecHash[segId2], segVecNormHash[segId2])
            sim = segfWeiHash[segId1] * segfWeiHash[segId2] * tSim
            segPairHash[segPair] = sim
#            print "similarity of segPair " + segPair + " : " + str(sim),
#            print " Text similarity: " + str(tSim)
            
    return segPairHash 

############################
## represent text string into tf-idf vector
def textSim(feaHash1, norm1, feaHash2, norm2):
    tSim = 0.0
    for seg in feaHash1:
        if seg in feaHash2:
            w1 = feaHash1[seg]
            w2 = feaHash2[seg]
            tSim += w1 * w2
    tSim = tSim / (norm1 * norm2)
#    print "text similarity: " + str(tSim)
#    if tSim == 0.0:
#        print "Error! textSimilarity is 0!"
#        print "vec1: " + str(norm1) + " ",
#        print feaHash1
#        print "vec2: " + str(norm2) + " ",
#        print feaHash2
    return tSim

############################
## represent text string into tf-idf vector
def toTFIDFVector(text, docNum):

    #[GUA] m_eSegTextHash mapping: segID -> twitterText(segment|segment|...)###twitterText###...
    #[GUA] segmentDFHash mapping: twitterNum
    docArr = text.split("###")
    docId = 0
    # one word(unigram) is a feature, not segment
    feaTFHash = {}
    feaAppHash = {}
    featureHash = {}
    norm = 0.0
    for docStr in docArr:
        docId += 1
        segArr = docStr.split("|")
        for segment in segArr:

            #[GUA] appHash mapping: docId -> 1/0
            #[GUA] feaAppHash mapping: segment -> [docId -> 1/0]
            #[GUA] feaTFHash mapping: segment -> segmentFreq
            if segmentForSim:
                appHash = {}
                if segment in feaTFHash:
                    feaTFHash[segment] += 1
                    appHash = feaAppHash[segment]
                else:
                    feaTFHash[segment] = 1
                appHash[docId] = 1
                feaAppHash[segment] = appHash
            else:
                wordArr = segment.split(" ")
                for word in wordArr:
                    appHash = {}
                    if word in feaTFHash:
                        feaTFHash[word] += 1
                        appHash = feaAppHash[word]
                    else:
                        feaTFHash[word] = 1
                    appHash[docId] = 1
                    feaAppHash[word] = appHash
    for word in feaTFHash:
#        tf = math.log(feaTFHash[word]*1.0 + 1.0)
#        idf = math.log((docNum + 1.0)/(len(feaAppHash[word]) + 0.5))
        tf = feaTFHash[word] 
        idf = math.log(TWEETNUM/wordDFHash[word])
        weight = tf*idf
        featureHash[word] = weight
        norm += weight * weight
    norm = math.sqrt(norm)


    #[GUA] featureHash mapping: segment -> tf-idf / interval
    return featureHash, norm

############################
## merge two hash: add smallHash's content into bigHash
def merge(smallHash, bigHash):
    print "Incorporate " + str(len(smallHash)) + " pairs into " + str(len(bigHash)),
    newNum = 0
    changeNum = 0
    for pair in smallHash:
        if pair in bigHash:
            bigHash[pair] += smallHash[pair]
            changeNum += 1
        else:
            bigHash[pair] = smallHash[pair]
            newNum += 1
    print " with newNum/changedNum " + str(newNum) + "/" + str(changeNum)
    return bigHash

############################
## cluster Event Segment
def geteSegPairSim(dataFilePath, M, toolDirPath):
    socialFeatureFile = open("/home/yanxia/SED/ni_data/timeCorrect/tweetSocialFeature01", "r")
    socialFeatureHash = cPickle.load(socialFeatureFile)
    socialFeatureFile2 = open("/home/yanxia/SED/ni_data/timeCorrect/tweetSocialFeature02", "r")
    socialFeatureHash2 = cPickle.load(socialFeatureFile2)
    socialFeatureHash.update(socialFeatureHash2)


    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        if item.find("segged_") != 0:
            continue
        print "### Processing " + item

        #[GUA] Time window
        tStr = item[len(item)-2:len(item)]
        if tStr not in validDays: continue
        print "Time window: " + tStr
        N_t = 0 # tweetNum appeared in time window tStr
        # load segged tweet files in time window tStr
        seggedFile = file(dataFilePath + item)
        # load extracted event segments in tStr
        eventSegFilePath = dataFilePath + "event" + UNIT + tStr

        #[GUA] segmentHash mapping: segment -> segID, segmentDFHash mapping: segID -> f_st
        [unitHash, unitDFHash] = loadEvtseg(eventSegFilePath)

        # load extracted createdHour of tweet in tStr
        tweetTimeFilePath = toolDirPath + "tweetTime" + tStr


        #[GUA] usrHour name: tweIdToUsrId + TimeWindow, format: twitterID -> hourStr([00, 23])
        #timeHash = loadTime(tweetTimeFilePath)

        m_docNum_Hash = {} # m: m_docNum
        m_eSegAppHash_Hash = {} # m:m_eSegAppHash
        m_eSegTextHash_Hash = {} # m:m_eSegTextHash
        #m_eSegAppHash = {} # event segments' appearHash in time interval m
        #m_eSegTextHash = {} # event segments' appeared in Text in time interval m

        m_step = 24 / M # split time window tStr into M parts

        while True:
            #[GUA] seggedFile name: * + TimeWindow, format: twitterID, *, twitterText(segment|segment|...), ...
            lineStr = seggedFile.readline()
            lineStr = re.sub(r'\n', " ", lineStr)
            lineStr = lineStr.strip()
            if len(lineStr) <= 0:
                break
            contentArr = lineStr.split("\t")
            tweetIDstr = contentArr[0]
            tweetText = contentArr[2]
            if len(tweetText)*len(tweetIDstr) == 0:
                print "Error: empty id or text: " + tweetIDstr + "#" + tweetText
                exit
            N_t += 1
            #hour = int(timeHash[tweetIDstr])
            hour = int(socialFeatureHash[tweetIDstr]["Time"])

            subTW_m = hour/m_step

            if subTW_m not in m_docNum_Hash: m_docNum_Hash[subTW_m] = 1
            else: m_docNum_Hash[subTW_m] += 1

            if subTW_m not in m_eSegTextHash_Hash: m_eSegTextHash = {}
            else: m_eSegTextHash = m_eSegTextHash_Hash[subTW_m]

            if subTW_m not in m_eSegAppHash_Hash: m_eSegAppHash = {}
            else: m_eSegAppHash = m_eSegAppHash_Hash[subTW_m]

#            print tweetIDstr + " is created at hour: " + str(hour)

            textArr = tweetText.split("|")
            for segment in textArr:

                if useSegmentFlag:
                    #[GUA] segmentHash mapping: segment -> segID, segmentDFHash mapping: segID -> f_st
                    if segment not in unitHash:
                        continue
                    # event segments
                    segId = unitHash[segment]
                    appTextStr = ""
                    apphash = {}
                    if segId in m_eSegAppHash:
                        apphash = m_eSegAppHash[segId]
                        appTextStr = m_eSegTextHash[segId]
                    if tweetIDstr in apphash:
                        continue
                    appTextStr += tweetText + "###"
                    apphash[tweetIDstr] = 1
                    m_eSegAppHash[segId] = apphash
                    m_eSegTextHash[segId] = appTextStr
                else:
                    wordArr = segment.split(" ")
                    for word in wordArr:
                        if word not in unitHash:
                            continue
                        # event segments
                        unitId = unitHash[word]
                        appTextStr = ""
                        apphash = {}
                        if unitId in m_eSegAppHash:
                            apphash = m_eSegAppHash[unitId]
                            appTextStr = m_eSegTextHash[unitId]
                        if tweetIDstr in apphash:
                            continue
                        appTextStr += tweetText + "###"
                        apphash[tweetIDstr] = 1
                        m_eSegAppHash[unitId] = apphash
                        m_eSegTextHash[unitId] = appTextStr
            m_eSegTextHash_Hash[subTW_m] = m_eSegTextHash 
            m_eSegAppHash_Hash[subTW_m] = m_eSegAppHash 

            if N_t % 100000 == 0:
                print "### " + str(time.asctime()) + " " + str(N_t) + " tweets are processed!"

        segPairHash = {} # all edges in graph
        for subTW_m in m_docNum_Hash:
            m_docNum = m_docNum_Hash[subTW_m]
            m_eSegTextHash =m_eSegTextHash_Hash[subTW_m]
            m_eSegAppHash = m_eSegAppHash_Hash[subTW_m]

            #[GUA] m_eSegAppHash mapping: segID -> [twitterID -> 1/0]
            #[GUA] m_eSegTextHash mapping: segID -> twitterText(segment|segment|...)###twitterText###...
            #[GUA] segmentDFHash mapping: segID -> f_st
            #[GUA] segmentDFHash mapping: twitterNum
            m_segPairHash = calSegPairSim(m_eSegAppHash, m_eSegTextHash, unitDFHash, m_docNum)
            segPairHash = merge(m_segPairHash, segPairHash)

        seggedFile.close()
        print "### " + str(time.asctime()) + " " + str(len(unitHash)) + " event segments in " + item + " are loaded. With segment pairs Num: " + str(len(segPairHash))
        
        segPairFile = file(dataFilePath + "segPairFile" + tStr, "w")
        cPickle.dump(unitHash, segPairFile)
        cPickle.dump(segPairHash, segPairFile)
        segPairFile.close()

############################
## keep top K (value) items in hash
def getTopItems(sampleHash, K):
    sortedList = sorted(sampleHash.items(), key = lambda a:a[1], reverse = True)
    sampleHash.clear()
    sortedList = sortedList[0:K]
    for key in sortedList:
        sampleHash[key[0]] = key[1]
    return sampleHash

############################
## main Function
global useSegmentFlag, UNIT
print "###program starts at " + str(time.asctime())
#dataFilePath = r"../Data_hfmon/segged_qtwe/"
#dataFilePath = r"../Data_hfmon/segged_ltwe/"
dataFilePath = r"/home/yanxia/SED/ni_data/word/"
toolDirPath = r"../Tools/"
# use segment or word as unit
useSegmentFlag = True
if useSegmentFlag:
    UNIT = "segment"
else:
    UNIT = "word"
global segmentForSim # useful only when useSegmentFlag = true
segmentForSim = True # worse performance than word
dfFilePath = dataFilePath + "word_df"
if segmentForSim:
    dfFilePath = dataFilePath + "segment_df"

wordDFHash = {}
TWEETNUM = 0
M = 12

devDays = ['06', '07', '08']
testDays = ['11', '12', '13', '14', '15']
global validDays
validDays = devDays + testDays

loadDF(dfFilePath)
geteSegPairSim(dataFilePath, M, toolDirPath)

print "###program ends at " + str(time.asctime())
