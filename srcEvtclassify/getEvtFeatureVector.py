#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import math
import cPickle
#from stemming.porter2 import stem
from nltk import stem
import sys

class Event:
    def __init__(self, eventId):
        self.eventId = eventId
        self.tweets = []
    
    def updateEvent(self, nodeHash, edgeHash):
        self.nodeHash = nodeHash
        self.edgeHash = edgeHash
        
    def setTweets(self, tweetStr):
        self.tweets.append(tweetStr)

############################
## load wikiGram
def loadWiki(filepath):
    global wikiProbHash
    inFile = file(filepath,"r")
    while True:
        lineStr = inFile.readline()
        lineStr = re.sub(r'\n', ' ', lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        prob = float(lineStr[0:lineStr.find(" ")])
        gram = lineStr[lineStr.find(" ")+1:len(lineStr)]
#        print gram + "\t" + str(prob)
        wikiProbHash[gram] = prob
    inFile.close()
    print "### " + str(time.asctime()) + " " + str(len(wikiProbHash)) + " wiki grams' prob are loaded from " + inFile.name

############################
## cluster Event Segment
def clusterEventSegment(kNeib, taoRatio):
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        if item.find("segged") != 0:
            continue
        tStr = item[len(item)-2:len(item)]
#        print "Time window: " + tStr
        eventDayFile = file(dataFilePath + "eventDayFile" + tStr, "wb")
        segPairFilePath = dataFilePath + "segPairFile" + tStr
        [segmentHash, segPairHash] = loadsegPair(segPairFilePath)
        print "### " + str(time.asctime()) + " " + str(len(segmentHash)) + " event segments in " + segPairFilePath  + " are loaded. With segment pairs Num: " + str(len(segPairHash))
        reverseSegHash = dict([(segmentHash[seg], seg) for seg in segmentHash.keys()]) # segid:segStr
        kNNHash = getkNN(segPairHash)
        print "### " + str(time.asctime()) + " " + str(len(kNNHash)) + " event segments' " + str(kNeib) + " neighbors are got."
        eventHash = clustering(kNNHash, segPairHash)
        print "### " + str(time.asctime()) + " " + str(len(eventHash)) + " events."
        [validEventHash, filteredEventHash, segmentNewWorthHash] = filtering(eventHash, reverseSegHash)
        print "### " + str(time.asctime()) + " Aft filtering " + str(len(validEventHash)) + " events are kept."
        cPickle.dump(validEventHash, eventDayFile)
        cPickle.dump(filteredEventHash, eventDayFile)
        cPickle.dump(segmentNewWorthHash, eventDayFile)
        eventDayFile.close()
        print "### " + str(time.asctime()) + " Events are written to " + eventDayFile.name

############################
## load seg pair
def loadsegPair(filepath):
    inFile = file(filepath,"r")
    segmentHash = cPickle.load(inFile)
    segPairHash = cPickle.load(inFile)
    inFile.close()
    return segmentHash, segPairHash

def getkNN(segPairHash):
    # get segments' k nearest neighbor
    kNNHash = {}
    for pair in segPairHash:
        sim = segPairHash[pair]
        segArr = pair.split("|")
        segId1 = int(segArr[0])
        segId2 = int(segArr[1])
        nodeSimHash = {}
        if segId1 in kNNHash:
            nodeSimHash = kNNHash[segId1]
        nodeSimHash[segId2] = sim
        if len(nodeSimHash) > kNeib:
            nodeSimHash = getTopItems(nodeSimHash, kNeib)
        kNNHash[segId1] = nodeSimHash

        nodeSimHash2 = {}
        if segId2 in kNNHash:
            nodeSimHash2 = kNNHash[segId2]
        nodeSimHash2[segId1] = sim
        if len(nodeSimHash2) > kNeib:
            nodeSimHash2 = getTopItems(nodeSimHash2, kNeib)
        kNNHash[segId2] = nodeSimHash2
    return kNNHash

def clustering(kNNHash, segPairHash):
    # cluster similar segments into events
    eventHash = {}
    eventIdx = 0
    nodeInEventHash = {}
    for segId1 in kNNHash:
        nodeSimHash = kNNHash[segId1]
#           print "#############################segId1: " + str(segId1)
#           print nodeSimHash
        for segId2 in nodeSimHash:
            if segId2 in nodeInEventHash:
                # s2 existed in one cluster, no clustering again
                continue
#               print "*************segId2: " + str(segId2)
#               print kNNHash[segId2]
            if segId1 in kNNHash[segId2]:
                # s1 s2 in same cluster

                #[GUA] edgeHash mapping: segId + | + segId -> simScore
                #[GUA] nodeHash mapping: segId -> edgeNum
                #[GUA] nodeInEventHash mapping: segId -> eventId
                eventId = eventIdx
                nodeHash = {}
                edgeHash = {}
                event = None
                if segId1 in nodeInEventHash:
                    eventId = nodeInEventHash[segId1]
                    event = eventHash[eventId]
                    nodeHash = event.nodeHash
                    edgeHash = event.edgeHash
                    nodeHash[segId1] += 1
                else:
                    eventIdx += 1
                    nodeInEventHash[segId1] = eventId
                    event = Event(eventId)
                    nodeHash[segId1] = 1
                nodeHash[segId2] = 1
                if segId1 < segId2:
                    edge = str(segId1) + "|" + str(segId2)
                else:
                    edge = str(segId2) + "|" + str(segId1)
                edgeHash[edge] = segPairHash[edge]
                event.updateEvent(nodeHash, edgeHash)
                eventHash[eventId] = event
                nodeInEventHash[segId2] = eventId
        # seg1's k nearest neighbors have been clustered into other events Or
        # seg1's k nearest neighbors all have long distance from seg1
        if segId1 in nodeInEventHash:
            continue
        eventId = eventIdx
        eventIdx += 1
        nodeHash = {}
        edgeHash = {}
        event = Event(eventId)
        nodeHash[segId1] = 1
        event.updateEvent(nodeHash, edgeHash)
        eventHash[eventId] = event
        nodeInEventHash[segId1] = eventId
    return eventHash

def filtering(eventHash, reverseSegHash):
    # filtering event by mu_e > 0; statistic segNum_max, edgeNum_max
    segmentNewWorthHash = {}
    mu_max = 0.0
    mu_eventHash = {}
    for eventId in sorted(eventHash.keys()):
        event = eventHash[eventId]
        nodeHash = event.nodeHash
        edgeHash = event.edgeHash
        segNum = len(nodeHash)
        mu_sum = 0.0
        sim_sum = 0.0
        contentArr = [reverseSegHash[id] for id in nodeHash]
        newWorHash = {}
        for segment in contentArr:
            mu_s = segNewWorth(segment)
            segmentNewWorthHash[segment] = mu_s
            newWorHash[segment] = mu_s
            mu_sum += mu_s

        #[GUA] edges between each segment in event? or only edges used for JP? I prefer the latter
        for edge in edgeHash:
            sim_sum += edgeHash[edge]
        mu_avg = mu_sum/segNum
        sim_avg = sim_sum/segNum
        mu_e = mu_avg * sim_avg
        if mu_e <= 0:
            continue
        mu_eventHash[eventId] = mu_e
        if mu_e > mu_max:
            mu_max = mu_e

        if False: # debug information
            print "### event " + str(eventId) + " node|edge: " + str(segNum) + "|" + str(len(edgeHash)) + " mu_e: " + str(mu_e) + " mu_avg: " + str(mu_avg) + " sim_avg: " + str(sim_avg)
            print sorted(newWorHash.items(), key = lambda a:a[1], reverse = True)

    print "### Aft filtering mu_e > 0 " + str(len(mu_eventHash)) + " events are kept. mu_max: " + str(mu_max)

    validEventHash = {}
    for eventId in mu_eventHash:
        mu_e = mu_eventHash[eventId]
        if mu_max * mu_e == 0:
            continue
#            print "### event " + str(eventId) +  " mu_e|ratio: " + str(mu_e) + "| " + str(mu_max/mu_e) + " status: ",
        validEventHash[eventId] = mu_max/mu_e
#### filterEventsByTaoRatio mu_max/mu_e < taoRatio
#           if mu_max/mu_e < taoRatio:
#               validEventHash[eventId] = mu_max/mu_e
    filteredEventHash = dict([(eId, eventHash[eId]) for eId in validEventHash])
    return validEventHash, filteredEventHash, segmentNewWorthHash

############################
## newsWorthiness
def segNewWorth(segment):
    wordArr = segment.split(" ")
    wordNum = len(wordArr)
    if wordNum == 1:
        if segment in wikiProbHash:
            return math.exp(wikiProbHash[segment])
        else:
            return 0.0
    maxProb = 0.0
    for i in range(0, wordNum):
        for j in range(i+1, wordNum+1):
            subArr = wordArr[i:j]
            prob = 0.0
            subS = " ".join(subArr)
            if subS in wikiProbHash:
                prob = math.exp(wikiProbHash[subS]) - 1.0
            if prob > maxProb:
                maxProb = prob
#    if maxProb > 0:
#        print "Newsworthiness of " + segment + " : " + str(maxProb)
    return maxProb

def calculateFeature(kNeib, taoRatio):
    global eventFile, eventVectorFile, eventDetailFile
    # output events and feature vector
    eventFile = file(dataFilePath + "EventFile" + "_k" + str(kNeib) + "t" + str(taoRatio), "w")
    eventVectorFile = file(dataFilePath + "EventVectorFile", "w")
    eventDetailFile = file(dataFilePath + "EventDetailFile", "w")
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        if item.find("segged") != 0:
            continue
        tStr = item[len(item)-2:len(item)]
        eventDayFileName = dataFilePath + "eventDayFile" + tStr
        [validEventHash, filteredEventHash, segmentNewWorthHash] = loadEventClusters(eventDayFileName)
        print "### " + str(time.asctime()) + " Events are loaded from " + eventDayFileName
        segPairFilePath = dataFilePath + "segPairFile" + tStr
        [segmentHash, segPairHash] = loadsegPair(segPairFilePath)
        print "### " + str(time.asctime()) + " " + str(len(segmentHash)) + " event segments in " + segPairFilePath  + " are loaded. With segment pairs Num: " + str(len(segPairHash))
        reverseSegHash = dict([(segmentHash[seg], seg) for seg in segmentHash.keys()]) # segid:segStr
        clusterFeature(validEventHash, filteredEventHash, segmentNewWorthHash, reverseSegHash, tStr)
    eventFile.close()
    eventVectorFile.close()
    eventDetailFile.close()
    print "### " + str(time.asctime()) + " k = " + str(kNeib) + ". Events detected are stored into " + eventFile.name
    print "### " + str(time.asctime()) + " k = " + str(kNeib) + ". Events vector are stored into " + eventVectorFile.name
    print "### " + str(time.asctime()) + " k = " + str(kNeib) + ". Events' tagwords and pastwords are stored into " + eventDetailFile.name

def loadEventClusters(eventDayFileName):
    eventDayFile = file(eventDayFileName , "rb")
    validEventHash = cPickle.load(eventDayFile)
    filteredEventHash = cPickle.load(eventDayFile)
    segmentNewWorthHash = cPickle.load(eventDayFile)
    eventDayFile.close()
    return validEventHash, filteredEventHash, segmentNewWorthHash

def splitIntoM(tweSFHash, N_t, Usr_t):
    N_t_list = []
    Usr_t_list = []
    if M == 1:
        return [N_t], [Usr_t]
    for m in range(M):
        m_tweetsInDay = dict([(tweetId, 1) for tweetId in tweSFHash if int(tweSFHash[tweetId]["Time"])%M == m])
        m_usrsInDay = dict([(tweSFHash[tweetId]["Usr"], 1) for tweetId in tweSFHash if int(tweSFHash[tweetId]["Time"])%M == m])
        m_N_t = len(m_tweetsInDay)
        m_Usr_t = len(m_usrsInDay)
        N_t_list.append(m_N_t)
        Usr_t_list.append(m_Usr_t)
    return N_t_list, Usr_t_list

def clusterFeature(validEventHash, filteredEventHash, segmentNewWorthHash, reverseSegHash, tStr):
    ## extra resource
    eventSegDFFilePath = dataFilePath + "event" + UNIT  + "DF" + tStr
    [N_t, Usr_t, unitDFHash, unitUsrHash] = loadesegDF(eventSegDFFilePath)
    tweetSocialFeatureFilePath = toolDirPath + "tweetSocialFeature" + tStr
    tweSFHash = loadsocialfeature(tweetSocialFeatureFilePath)
    [N_t_list, Usr_t_list] = splitIntoM(tweSFHash, N_t, Usr_t)
    print "### Tweets In Day" + tStr + ": " + str(N_t_list)
    print "### Usrs In Day" + tStr + ": " + str(Usr_t_list)
    tweetTimeFilePath = toolDirPath + "tweetTime" + tStr
#    timeHash = loadTime(tweetTimeFilePath)
    [segNum_max, edgeNum_max, tweetNum_max, usrNum_max, wiki_max, sim_max] = getMaxValuesForFeatures(filteredEventHash, reverseSegHash, unitDFHash, unitUsrHash, segmentNewWorthHash)
    sortedEventlist = sorted(validEventHash.items(), key = lambda a:a[1])
    eventNum = 0
    for eventItem in sortedEventlist:
        eventNum += 1
        eventId = eventItem[0]
        eventStr = tStr + "_" + str(eventNum)
        event = filteredEventHash[eventId]
        edgeHash = event.edgeHash
        nodeHash = event.nodeHash
        segList = [reverseSegHash[id] for id in nodeHash]
## calculate event's feature vector
        eventVec = {}
        [tweetHash, usrHash, tweetNum, usrNum] = getRelTweets(segList, unitDFHash, unitUsrHash)
        [dupNum, stemWordHash] = getDupWords(segList)

        wiki_avg = sum([segmentNewWorthHash[seg] for seg in segList])/len(segList)
        sim_avg = sum(event.edgeHash.values())/len(segList)
        ratio = eventItem[1]
 #       feature1 = 1.0/ratio #v1
        feature1 = wiki_avg/wiki_max #v2
        feature17 = sim_avg/sim_max
        feature11 = dupNum*1.0/len(stemWordHash) #v2
        feature2 = len(nodeHash)*1.0 / segNum_max
        feature3 = len(edgeHash)*1.0 / edgeNum_max
        feature4 = (len(nodeHash)-1)*1.0 / len(edgeHash)

        sumFlag = True
        if sumFlag: #sum up feature values in m
            value = 0.0
        else: # multiply
            value = 1.0
        [feature5, feature6, feature7, feature8, feature9, feature10, feature12, feature13, feature14, feature15, feature16] = initiate(value)
        
        for m in range(M):
            if N_t_list[m] == 0:
                print "m: " + str(m+1) + " | tweet 0, usr 0, tweetDay 0, usrDay 0"
                continue
            if M == 1:
                m_tweetHash = tweetHash
                m_usrHash = usrHash
            else:
                m_tweetHash = dict([(tweetId, 1) for tweetId in tweetHash if int(tweSFHash[tweetId]["Time"])%M == m])
                m_usrHash = dict([(tweSFHash[tweetId]["Usr"], 1) for tweetId in tweetHash if int(tweSFHash[tweetId]["Time"])%M == m])
            m_tweetNum = len(m_tweetHash)
            m_usrNum = len(m_usrHash) 
            print "m: " + str(m+1) + " " + str(m_tweetNum) + " " + str(m_usrNum) + " " + str(N_t_list[m]) + " " + str(Usr_t_list[m])
            m_fea5 = m_tweetNum*1.0/ N_t_list[m]  #v1
            m_fea6 = m_usrNum*1.0/ Usr_t_list[m] #v1
#            m_fea5 = m_tweetNum*1.0/ m_tweetNum_max #v2
#            m_fea6 = m_usrNum*1.0/ m_usrNum_max  #v2
            feature5 = increase(feature5, m_fea5, sumFlag)
            feature6 = increase(feature6, m_fea6, sumFlag)
            if len(m_tweetHash) > 0:
                validTweetHash = dict([(tid, 1) for tid in m_tweetHash if tid in tweSFHash])
                rthash = dict([(tid, 1) for tid in validTweetHash if tweSFHash[tid]["RT"] == True])
                menhash = dict([(tid, 1) for tid in validTweetHash if tweSFHash[tid]["Men"] == True])
                replyhash = dict([(tid, 1) for tid in validTweetHash if tweSFHash[tid]["Reply"] == True])
                urlhash = dict([(tid, 1) for tid in validTweetHash if tweSFHash[tid]["Url"] == True])
                favhash = dict([(tid, 1) for tid in validTweetHash if tweSFHash[tid]["Fav"] == True])
                taghash = dict([(tid, tweSFHash[tid]["Tag"]) for tid in validTweetHash if len(tweSFHash[tid]["Tag"]) > 0])
                pasthash = dict([(tid, tweSFHash[tid]["Past"]) for tid in validTweetHash if len(tweSFHash[tid]["Past"]) > 0])

                feature7 = increase(feature7, len(rthash)*1.0/len(m_tweetHash), sumFlag)
                feature8 = increase(feature8, len(menhash)*1.0/len(m_tweetHash), sumFlag)
                feature9 = increase(feature9, len(replyhash)*1.0/len(m_tweetHash), sumFlag)
                feature10 = increase(feature10, len(urlhash)*1.0/len(m_tweetHash), sumFlag)
    #            feature11 = increase(feature11, len(favhash)*1.0/len(m_tweetHash), sumFlag) #v1
                feature12 = increase(feature12, len(taghash)*1.0/len(m_tweetHash), sumFlag)
                feature13 = increase(feature13, len(pasthash)*1.0/len(m_tweetHash), sumFlag)

                if len(taghash) > 0:
                    tagMap = getWordTF(taghash)
                    currfreqTag = dict([(tag, 0) for tag in freqTagHash])
                    currfreqTagPrf = dict([(tag, 0) for tag in freqPrefixHash])
                    currfreqTagSfx = dict([(tag, 0) for tag in freqSuffixHash])
                    for tag in tagMap:
                        if tag in currfreqTag:
                            currfreqTag[tag] = 1
                        for i in xrange(len(tag) - 1):
                            prefix = tag[1:i+2]
                            suffix = tag[i+1:len(tag)]
                            if prefix in currfreqTagPrf:
                                currfreqTagPrf[prefix] = 1
        #                        print "contain prefix " + prefix
                            if suffix in currfreqTagSfx:
                                currfreqTagSfx[suffix] = 1
        #                        print "contain suffix " + suffix
                if not lexicon:
                    feature14 = increase(feature14, sum(currfreqTag.values())*1.0/len(tagMap), sumFlag)
                    feature15 = increase(feature15, sum(currfreqTagPrf.values())*1.0/len(tagMap), sumFlag)
                    feature16 = increase(feature16, sum(currfreqTagSfx.values())*1.0/len(tagMap), sumFlag)
                else:
                    feature14.update(currfreqTag)
                    feature15.update(currfreqTagPrf)
                    feature16.update(currfreqTagSfx)
        if sumFlag:
            feature5 /= M
            feature6 /= M
            feature7 /= M
            feature8 /= M
            feature9 /= M
            feature10 /= M
            feature12 /= M
            feature13 /= M
            feature14 /= M
            feature15 /= M
            feature16 /= M
    ## output events' vector into file
        eventVec["01mue"] = feature1
        eventVec["17sim"] = feature17
        eventVec["02seg"] = feature2
        eventVec["03edg"] = feature3
        eventVec["04sve"] = feature4
        eventVec["05dfe"] = feature5
        eventVec["06udf"] = feature6
        eventVec["07rtm"] = feature7
        eventVec["08men"] = feature8
        eventVec["09rep"] = feature9
        eventVec["10url"] = feature10
#        eventVec["11fav"] = feature11 #v1
        eventVec["11dup"] = feature11 #v2
        eventVec["12tag"] = feature12
        eventVec["13pst"] = feature13
        eventVec["14ftg"] = feature14
        eventVec["15prf"] = feature15
        eventVec["16sfx"] = feature16
        print sorted(eventVec.items(), key = lambda a:a[0])

        # for output in eventDetailFile
#        print "Evtfea vec: " + eventVec
#        pastMap = getWordTF(pasthash)
        cPickle.dump("###Event " + eventStr + " nodes:" + str(len(nodeHash)) + " edges:" + str(len(edgeHash)), eventVectorFile)
        cPickle.dump(eventVec, eventVectorFile)    
        outputEvents(eventStr, nodeHash, edgeHash, stemWordHash, eventVec, eventItem[1], segmentNewWorthHash, reverseSegHash) 

def initiate(value):
    feature5 = value
    feature6 = value
    feature7 = value
    feature8 = value
    feature9 = value
    feature10 = value
    feature12 = value
    feature13 = value
    feature14 = value
    feature15 = value
    feature16 = value
    return feature5, feature6, feature7, feature8, feature9, feature10, feature12, feature13, feature14, feature15, feature16

def increase(feature, step, sumFlag):
    if step == 0:
        return feature
    if sumFlag:
        feature += step
    else:
        feature *= step
    return feature
############################
## load event seg df
def loadesegDF(filepath):
    inFile = file(filepath,"r")
    N_t = cPickle.load(inFile)
    Usr_t = cPickle.load(inFile)
    unitDFHash = cPickle.load(inFile)
    unitUsrHash = cPickle.load(inFile)
    inFile.close()
    print "### " + str(time.asctime()) + " " + str(len(unitDFHash)) + " event units' df and usrDf are loaded from " + inFile.name
    return N_t, Usr_t, unitDFHash, unitUsrHash

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
## load tweetID-createdHour
def loadTime(filepath):
    inFile = file(filepath,"r")
    timeHash = cPickle.load(inFile)
    inFile.close()
    return timeHash

def getDupWords(segList):
    # stemmed words in current event
    stemWordHash = {}
    for seg in segList:
        for word in seg.split(" "):
            stemWord = stemmer.stem(word)
            if stemWord in stemWordHash:
                stemWordHash[stemWord] += 1
            else:
                stemWordHash[stemWord] = 1
    dupNum = 0
    for word in stemWordHash:
        if stemWordHash[word] > 1:
            dupNum += 1
    return dupNum, stemWordHash

def getMaxValuesForFeatures(filteredEventHash, reverseSegHash, unitDFHash, unitUsrHash, segmentNewWorthHash):
    segNum_max = 0
    edgeNum_max = 0
    tweetNum_max = 0
    usrNum_max = 0
    wiki_max = 0.0
    sim_max = 0.0
    for eventId in filteredEventHash:
        event = filteredEventHash[eventId]
        segList = [reverseSegHash[id] for id in event.nodeHash]
        [tweetHash, usrHash, tweetNum, usrNum] = getRelTweets(segList, unitDFHash, unitUsrHash)
        # calculate segNum_max, edgeNum_max
        segNum = len(event.nodeHash)
        edgeNum = len(event.edgeHash)
        wiki_avg = sum([segmentNewWorthHash[seg] for seg in segList])/len(segList)
        sim_avg = sum(event.edgeHash.values())/len(segList)
        segNum_max = getbigger(segNum, segNum_max)
        edgeNum_max = getbigger(edgeNum, edgeNum_max)
        tweetNum_max = getbigger(tweetNum, tweetNum_max)
        usrNum_max = getbigger(usrNum, usrNum_max)
        wiki_max = getbigger(wiki_avg, wiki_max)
        sim_max = getbigger(sim_avg, sim_max)
    print "### SegNum_max: " + str(segNum_max) + " edgeNum_max: " + str(edgeNum_max) + " tweetNum_max: " + str(tweetNum_max) + " usrNum_max: " + str(usrNum_max)
    return segNum_max, edgeNum_max, tweetNum_max, usrNum_max, wiki_max, sim_max

def getRelTweets(segList, unitDFHash, unitUsrHash):
    # how many tweets are related to current event
    # how many users are related to current event
    tweetHash = {}
    usrHash = {}
    tweetNum = 1
    usrNum = 1
    for seg in segList:
        dfHash = unitDFHash[seg]
        tweetHash.update(dfHash)
        udfHash = unitUsrHash[seg]
        usrHash.update(udfHash)
        if False: # v2_0 for feature 5, 6 --> a little helpful, not used
            tweetNum *= len(dfHash)
            usrNum *= len(udfHash)
        if False: # v2 for feature 5, 6 --> a little helpful, not used
            tweetNum += math.log(len(dfHash))
            usrNum += math.log(len(udfHash))
    if minNumSegsInRelatedTweet > 1: # related tweet --> contains at least minNumSegsInRelatedTweet segs
        tidlist = tweetHash.keys()
        for tid in tidlist:
            segsContained = 0
            for seg in segList:
                if tid in unitDFHash[seg]:
                    segsContained += 1
            if segsContained < minNumSegsInRelatedTweet:
                del tweetHash[tid]
    if True: # v1 for feature 5, 6 --> original version
        tweetNum = len(tweetHash)
        usrNum = len(usrHash)
    return tweetHash, usrHash, tweetNum, usrNum

def statisticWithTao(validEventHash):# statistic information about events
    eventNumHash = {}
    for eventId in validEventHash:
        ratioInt = int(validEventHash[eventId])
        if ratioInt in eventNumHash:
            eventNumHash[ratioInt] += 1
        else:
            eventNumHash[ratioInt] = 1
    print "*************** " + str(len(validEventHash)) + " events, taoRatio " + str(taoRatio) + ", k " + str(kNeib)
    print "Event num < ratio: ",
    for ratioInt in sorted(eventNumHash.keys()):
        if ratioInt-1 in eventNumHash:
            eventNumHash[ratioInt] += eventNumHash[ratioInt-1]
    print sorted(eventNumHash.items(), key = lambda a:a[0])

def getbigger(num, num_max):
    if num > num_max:
        num_max = num
    return num_max

def getWordTF(wordApphash):
    tfMap = {}
    for tid in wordApphash.keys():
        wordStr = wordApphash[tid]
        wordArr = wordStr.split(" ")
        for word in wordArr:
            word = word.lower()
            if word in tfMap:
                tfMap[word] += 1
            else:
                tfMap[word] = 1
    return tfMap

def outputEvents(eventStr, nodeHash, edgeHash, stemWordHash, eventVec, score, segmentNewWorthHash, reverseSegHash):
    nodeNewWorthHash = dict([(segId, segmentNewWorthHash[reverseSegHash[segId]]) for segId in nodeHash])
    rankedNodeList_byNewWorth = sorted(nodeNewWorthHash.items(), key = lambda a:a[1], reverse = True)
    segList_byNewWorth = [reverseSegHash[key[0]] for key in rankedNodeList_byNewWorth]
    rankedNodeList = sorted(nodeHash.items(), key = lambda a:a[1], reverse = True)
    newNodeList = [key[0] for key in rankedNodeList]
    segList = [reverseSegHash[id] for id in newNodeList]
    ## output events into file
    eventDetailFile.write("****************************************\n###Event " + eventStr + " ratio: " + str(score))
    eventDetailFile.write( " " + str(len(segList)) + " nodes and " + str(len(edgeHash)) + " edges.\n")
    eventDetailFile.write(str(sorted(eventVec.items(), key = lambda a:a[0])) + "\n")
    eventDetailFile.write(str(sorted(stemWordHash.items(), key = lambda a:a[1], reverse = True)) + "\n")
#    eventDetailFile.write(str(len(taghash)) + " tweets; " +  str(len(tagMap)) + " tags; " + str(sorted(tagMap.items(), key = lambda a:a[1], reverse = True))+ "\n")
#    eventDetailFile.write(str(len(pasthash)) + " tweets; " +  str(len(pastMap)) + " tags; " + str(sorted(pastMap.items(), key = lambda a:a[1], reverse = True))+ "\n")
    eventFile.write("****************************************\n###Event " + eventStr + " ratio: " + str(score))
    eventFile.write(" " + str(len(segList)) + " nodes and " + str(len(edgeHash)) + " edges.\n")
    eventFile.write(str(rankedNodeList) + "\n")
    eventFile.write("||".join(segList) + "\n")
    eventFile.write("||".join(segList_byNewWorth) + "\n")
    eventFile.write(str(edgeHash) + "\n")
    if True:
        print "#################### event " + eventStr + " ratio: " + str(score),
        print " " + str(len(segList)) + " nodes and " + str(len(edgeHash)) + " edges."
        print rankedNodeList
        print "|".join(segList)
        print segList_byNewWorth
        print stemWordHash
        print str(edgeHash)
        
def loadFreqTags():
    global freqTagHash, freqPrefixHash, freqSuffixHash
    freqHashTagPath = toolDirPath + "freqHashTag"
    freqPrefixTagPath = toolDirPath + "freqPrefixTag"
    freqSuffixTagPath = toolDirPath + "freqSuffixTag"
    freqTagHash = loadFreqtag(freqHashTagPath)
    freqPrefixHash = loadFreqtag(freqPrefixTagPath)
    freqSuffixHash = loadFreqtag(freqSuffixTagPath)
    freqTagHash = getTopItems(freqTagHash, FreqTagNum)
    freqPrefixHash = getTopItems(freqPrefixHash, FreqTagNum)
    freqSuffixHash = getTopItems(freqSuffixHash, FreqTagNum)
    print "### Top " + str(FreqTagNum) + " frequent hashtag items(prefix|suffix) are selected."

def loadFreqtag(filePath):
    tagHash = {}
    inFile = file(filePath,"r")
    while True:
        lineStr = inFile.readline()
        lineStr = re.sub(r'\n', '', lineStr)
        if len(lineStr) <= 0:
            break
        arr = lineStr.split("\t")
        tf = float(arr[1])
        gram = arr[0].lower()
#        print gram + "\t" + str(prob)
        tagHash[gram] = tf
    inFile.close()
    print "### " + str(time.asctime()) + " " + str(len(tagHash)) + " items are loaded from " + inFile.name
    return tagHash

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
if len(sys.argv) == 1:
    print "Usage python getEvtFeatureVector.py [-c -f -min]"
    print "-c: clustering\t-f featurevectors\t-min minNumSegsInRelatedTweet"
    sys.exit()
global dataFilePath, toolDirPath
global useSegmentFlag, UNIT, FreqTagNum, stemmer, lexicon, minNumSegsInRelatedTweet, M
stemmer = stem.PorterStemmer()
wikiProbHash = {}
print "###program starts at " + str(time.asctime())
dataFilePath = r"../Data_hfmon/segged_ltwe/"
toolDirPath = r"../Tools/"
wikiPath = toolDirPath + "anchorProbFile_all"
kNeib = 5
taoRatio = 999 # not used, only used for twevent baseline
FreqTagNum = 2000
M = 1
# use segment or word as unit
useSegmentFlag = True 
if useSegmentFlag:
    UNIT = "segment"
else:
    UNIT = "word"
# whether use lexicon of frequent hashtags or number
lexicon = False
print "###Use lexicon feature: " + str(lexicon)

if "-c" in sys.argv: # clustering
    loadWiki(wikiPath)
    clusterEventSegment(kNeib, taoRatio)
if "-f" in sys.argv: # get feature vectors for event clusters
    loadFreqTags()
    minNumSegsInRelatedTweet = 1
    if "-min" in sys.argv:
        minNumSegsInRelatedTweet = int(sys.argv[sys.argv.index("-min")+1])
    print "### minNumSegsInRelatedTweet: " + str(minNumSegsInRelatedTweet)
    calculateFeature(kNeib, taoRatio)

print "###program ends at " + str(time.asctime())
