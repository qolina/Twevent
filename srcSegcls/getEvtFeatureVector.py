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
        self.tweets = []
    
    def updateEvent(self, nodeHash, edgeHash):
        self.nodeHash = nodeHash
        self.edgeHash = edgeHash
        
    def setTweets(self, tweetStr):
        self.tweets.append(tweetStr)

############################
## load seg pair
def loadsegPair(filepath):
    inFile = file(filepath,"r")
    segmentHash = cPickle.load(inFile)
    segPairHash = cPickle.load(inFile)
    inFile.close()
    return segmentHash, segPairHash

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
## keep top K (value) items in hash
def getTopItems(sampleHash, K):
    sortedList = sorted(sampleHash.items(), key = lambda a:a[1], reverse = True)
    sampleHash.clear()
    sortedList = sortedList[0:K]
    for key in sortedList:
        sampleHash[key[0]] = key[1]
    return sampleHash

############################
## cluster Event Segment
def clusterEventSegment(dataFilePath, toolDirPath, kNeib, taoRatio):
    fileList = os.listdir(dataFilePath)
    # output events and feature vector
    eventFile = file(dataFilePath + "EventFile" + "_k" + str(kNeib) + "t" + str(taoRatio), "w")
    eventVectorFile = file(dataFilePath + "EventVectorFile", "w")
    eventDetailFile = file(dataFilePath + "EventDetailFile", "w")
    for item in sorted(fileList):
        if item.find("segged") != 0:
            continue
        tStr = item[len(item)-2:len(item)]
#        print "Time window: " + tStr
        segPairFilePath = dataFilePath + "segPairFile" + tStr
        [segmentHash, segPairHash] = loadsegPair(segPairFilePath)

        print "### " + str(time.asctime()) + " " + str(len(segmentHash)) + " event segments in " + segPairFilePath  + " are loaded. With segment pairs Num: " + str(len(segPairHash))

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
        print "### " + str(time.asctime()) + " " + str(len(kNNHash)) + " event segments' " + str(kNeib) + " neighbors are got."

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
        print "### " + str(time.asctime()) + " " + str(len(eventHash)) + " events are got with nodes " + str(len(nodeInEventHash))

        # filtering event by mu_e > 0; statistic segNum_max, edgeNum_max
        reverseSegHash = dict([(segmentHash[seg], seg) for seg in segmentHash.keys()])
        segmentNewWorthHash = {}
        mu_max = 0.0
        segNum_max = 0.0
        edgeNum_max = 0.0
        mu_eventHash = {}
        for eventId in sorted(eventHash.keys()):
            event = eventHash[eventId]
            nodeList = event.nodeHash.keys()
            edgeHash = event.edgeHash
            segNum = len(nodeList)
            mu_sum = 0.0
            sim_sum = 0.0
            contentArr = [reverseSegHash[id] for id in nodeList]
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

            # segNum_max, edgeNum_max
            segNum = len(nodeList)
            edgeNum = len(edgeHash)
            if segNum > segNum_max:
                segNum_max = segNum
            if edgeNum > edgeNum_max:
                edgeNum_max = edgeNum
        print "### Aft filtering mu_e > 0 " + str(len(mu_eventHash)) + " events are kept. mu_max: " + str(mu_max) + " segNum_max: " + str(segNum_max) + " edgeNum_max: " + str(edgeNum_max)

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
        
        ## extra resource
        eventSegDFFilePath = dataFilePath + "event" + UNIT  + "DF" + tStr
        [N_t, Usr_t, unitDFHash, unitUsrHash] = loadesegDF(eventSegDFFilePath)
        tweetSocialFeatureFilePath = toolDirPath + "tweetSocialFeature" + tStr
        tweSFHash = loadsocialfeature(tweetSocialFeatureFilePath)


        sortedEventlist = sorted(validEventHash.items(), key = lambda a:a[1])
        eventNum = 0
        nodeLenHash = {}
        eventNumHash = {}
        for eventItem in sortedEventlist:
            eventNum += 1
            eventId = eventItem[0]
            event = filteredEventHash[eventId]
            edgeHash = event.edgeHash
            nodeHash = event.nodeHash
            nodeList = event.nodeHash.keys()
            nodeNewWorthHash = dict([(segId, segmentNewWorthHash[reverseSegHash[segId]]) for segId in nodeList])
            rankedNodeList_byNewWorth = sorted(nodeNewWorthHash.items(), key = lambda a:a[1], reverse = True)
            rankedNodeList = sorted(nodeHash.items(), key = lambda a:a[1], reverse = True)
            newNodeList = [key[0] for key in rankedNodeList]
            segList = [reverseSegHash[id] for id in newNodeList]
            segList_byNewWorth = [reverseSegHash[key[0]] for key in rankedNodeList_byNewWorth]
    ## calculate event's feature vector
            eventVec = {}
            # how many tweets are related to current event
            tweetHash = {}
            usrHash = {}
            for seg in segList:
                dfHash = unitDFHash[seg]
                tweetHash.update(dfHash)
                udfHash = unitUsrHash[seg]
                usrHash.update(udfHash)

    ## output events' vector into file
            ratio = eventItem[1]
            feature1 = ratio
            feature2 = len(nodeHash)*1.0 / segNum_max
            feature3 = len(edgeHash)*1.0 / edgeNum_max
            feature4 = (len(nodeHash)-1)*1.0 / len(edgeHash)
            feature5 = len(tweetHash)*1.0/ N_t
            feature6 = len(usrHash)*1.0/ Usr_t
            validTweetHash = dict([(tid, 1) for tid in tweetHash if tid in tweSFHash])
            rthash = dict([(tid, 1) for tid in validTweetHash if tweSFHash[tid]["RT"] == True])
            menhash = dict([(tid, 1) for tid in validTweetHash if tweSFHash[tid]["Men"] == True])
            replyhash = dict([(tid, 1) for tid in validTweetHash if tweSFHash[tid]["Reply"] == True])
            urlhash = dict([(tid, 1) for tid in validTweetHash if tweSFHash[tid]["Url"] == True])
            favhash = dict([(tid, 1) for tid in validTweetHash if tweSFHash[tid]["Fav"] == True])
            taghash = dict([(tid, tweSFHash[tid]["Tag"]) for tid in validTweetHash if len(tweSFHash[tid]["Tag"]) > 0])
            pasthash = dict([(tid, tweSFHash[tid]["Past"]) for tid in validTweetHash if len(tweSFHash[tid]["Past"]) > 0])
            feature7 = len(rthash)*1.0/len(tweetHash)
            feature8 = len(menhash)*1.0/len(tweetHash)
            feature9 = len(replyhash)*1.0/len(tweetHash)
            feature10 = len(urlhash)*1.0/len(tweetHash)
            feature11 = len(favhash)*1.0/len(tweetHash)
            feature12 = len(taghash)*1.0/len(tweetHash)
            feature13 = len(pasthash)*1.0/len(tweetHash)
            
            eventVec["01mue"] = feature1
            eventVec["02seg"] = feature2
            eventVec["03edg"] = feature3
            eventVec["04sve"] = feature4
            eventVec["05dfe"] = feature5
            eventVec["06udf"] = feature6
            eventVec["07rtm"] = feature7
            eventVec["08men"] = feature8
            eventVec["09rep"] = feature9
            eventVec["10url"] = feature10
            eventVec["11fav"] = feature11
            eventVec["12tag"] = feature12
            eventVec["13pst"] = feature13
#            print "Evtfea vec: " + eventVec
#            print "Past words: " + len(pasthash) + " " + str(pasthash)
            tagMap = {}
            pastMap = {}
            for tid in taghash.keys():
                tagStr = taghash[tid]
                tagArr = tagStr.split(" ")
                for tag in tagArr:
                    if tag in tagMap:
                        tagMap[tag] += 1
                    else:
                        tagMap[tag] = 1
            for tid in pasthash.keys():
                pastStr = pasthash[tid]
                pastArr = pastStr.split(" ")
                for pword in pastArr:
                    if pword in pastMap:
                        pastMap[pword] += 1
                    else:
                        pastMap[pword] = 1
            cPickle.dump("###Event " + tStr + "_" + str(eventNum) + " nodes:" + str(len(nodeList)) + " edges:" + str(len(edgeHash)), eventVectorFile)
            cPickle.dump(eventVec, eventVectorFile)    
            eventDetailFile.write("****************************************\n###Event " + tStr + "_" + str(eventNum) + " ratio: " + str(eventItem[1]))
            eventDetailFile.write( " " + str(len(nodeList)) + " nodes and " + str(len(edgeHash)) + " edges.\n")
            eventDetailFile.write(str(sorted(eventVec.items(), key = lambda a:a[0])) + "\n")
            eventDetailFile.write(str(len(taghash)) + " tweets; " +  str(len(tagMap)) + " tags; " + str(sorted(tagMap.items(), key = lambda a:a[1], reverse = True))+ "\n")
            eventDetailFile.write(str(len(pasthash)) + " tweets; " +  str(len(pastMap)) + " tags; " + str(sorted(pastMap.items(), key = lambda a:a[1], reverse = True))+ "\n")

    ## output events into file
            nodes = len(nodeList)
            if nodes in nodeLenHash:
                nodeLenHash[nodes] += 1
            else:
                nodeLenHash[nodes] = 1
            if True:
                print "#################### event " + str(eventId) + " ratio: " + str(eventItem[1]),
                print " " + str(len(nodeList)) + " nodes and " + str(len(edgeHash)) + " edges."
                print rankedNodeList
                print "|".join(segList)
                print segList_byNewWorth
                print str(edgeHash)
            eventFile.write("****************************************\n###Event " + tStr + "_" + str(eventNum) + " ratio: " + str(eventItem[1]))
            eventFile.write( " " + str(len(nodeList)) + " nodes and " + str(len(edgeHash)) + " edges.\n")
            eventFile.write(str(rankedNodeList) + "\n")
            eventFile.write("||".join(segList) + "\n")
            eventFile.write("||".join(segList_byNewWorth) + "\n")
            eventFile.write(str(edgeHash) + "\n")
            ratioInt = int(eventItem[1])
#            if ratioInt > 10:
#                continue
            if ratioInt in eventNumHash:
                eventNumHash[ratioInt] += 1
            else:
                eventNumHash[ratioInt] = 1

        print "*************** " + str(len(filteredEventHash)) + " events, taoRatio " + str(taoRatio) + ", k " + str(kNeib)
        print "Event num < ratio: ",
        for ratioInt in sorted(eventNumHash.keys()):
            if ratioInt-1 in eventNumHash:
                eventNumHash[ratioInt] += eventNumHash[ratioInt-1]
        print sorted(eventNumHash.items(), key = lambda a:a[0])
        print "Event contained nodes num distribution: ",
        print sorted(nodeLenHash.items(), key = lambda a:a[1], reverse = True)
    eventFile.close()
    eventVectorFile.close()
    eventDetailFile.close()
    print "### " + str(time.asctime()) + " k = " + str(kNeib) + ". Events detected are stored into " + eventFile.name
    print "### " + str(time.asctime()) + " k = " + str(kNeib) + ". Events vector are stored into " + eventVectorFile.name
    print "### " + str(time.asctime()) + " k = " + str(kNeib) + ". Events' tagwords and pastwords are stored into " + eventDetailFile.name

############################
## newsWorthiness
def segNewWorth(segment):
    wordArr = segment.split(" ")
    wordNum = len(wordArr)
    if wordNum == 1:
        if segment in wikiProbHash:

            #[GUA] should be math.exp(wikiProbHash[segment]) - 1
            return math.exp(wikiProbHash[segment])
        else:
            return 0.0
    maxProb = 0.0

    #[GUA] wordNum + 1 ? why? correct, but confused
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
############################
## main Function
global useSegmentFlag, UNIT
wikiProbHash = {}
print "###program starts at " + str(time.asctime())
#dataFilePath = r"../Data_hfmon/segged_qtwe/"
dataFilePath = r"../Data_hfmon/segged_ltwe/"
#dataFilePath = r"../Data_hfmon/segged_ltwe_hash/"
toolDirPath = r"../Tools/"
wikiPath = toolDirPath + "anchorProbFile_all"
kNeib = 5
taoRatio = 999 # not used
# use segment or word as unit
useSegmentFlag = True 
if useSegmentFlag:
    UNIT = "segment"
else:
    UNIT = "word"
loadWiki(wikiPath)
clusterEventSegment(dataFilePath, toolDirPath, kNeib, taoRatio)

print "###program ends at " + str(time.asctime())
