import sys
import time
import cPickle
from collections import Counter

import numpy as np
from sklearn.metrics import pairwise
from zpar import ZPar
from nltk.stem.porter import PorterStemmer

sys.path.append("/home/yanxia/SED/src/util/")
import snpLoader
import stringUtil as strUtil

class Event:
    def __init__(self, eventId):
        self.eventId = eventId
    
    def updateEvent(self, nodeHash, edgeHash):
        self.nodeHash = nodeHash
        self.edgeHash = edgeHash


def normTweetWords(word):
    normFinWords = {"est":"estimate", "rev":"revenue"}
    if word in normFinWords:
        return normFinWords[word]
    return word

def dayNewsExtr(newsDayWindow, newsSeqDayHash, vecNews, dayNews, newsSeqComp):
    newsSeqIdDay = sorted([newsSeqId for newsSeqId, dayInt in newsSeqDayHash.items() if dayInt in newsDayWindow])
    vecNewsDay = vecNews[newsSeqIdDay,:]
    textNewsDay = []
    for item in newsDayWindow:
        textNewsDay.extend(dayNews[item])
    newsSeqCompDay = [newsSeqComp[newsSeqId] for newsSeqId in newsSeqIdDay]
    return vecNewsDay, textNewsDay, newsSeqCompDay


def tClusterMatchNews_content(newsSeqCompDay, textNewsDay, textsIn, compsIn):
    stemmer = PorterStemmer()
    matchedNews_c = []
    newsMatchComp = [newsIdx for comp in compsIn for newsIdx, newsComps in enumerate(newsSeqCompDay) for newsCompItem in newsComps if comp[1] == newsCompItem[0]]
    for newsIdx in newsMatchComp:
        ncomps, nText, nValidWords = textNewsDay[newsIdx]
        nCompsWords = " ".join([comp[0] for comp in ncomps]).split()
        #print "--news", ncomps, nText, nValidWords, nCompsWords

        tWords = textsIn.split()
        tWords = [normTweetWords(word) for word in tWords]
        tWords = set([stemmer.stem(word) for word in tWords if word not in nCompsWords])
        #print "--tweetWords stem", sorted(list(tWords))

        commonWords = (tWords & set(nValidWords))# - set(nCompsWords)
        if len(commonWords) == 0: continue

        #print newsIdx, commonWords
        matchedNews_c.append(newsIdx)

    if len(matchedNews_c) == 0:
        return None
    return matchedNews_c

def getNgramComp(compName):
    words = compName.split()
    grams = []
    for i in range(len(words)):
        for j in range(i, len(words)):
            if i == j and words[i] == "&": continue
            grams.append(" ".join(words[i:j+1]))
    return set(grams)


def findComp_name(headline, snp_comp):
    matchedComp = [(gram, compName) for compName in snp_comp for gram in getNgramComp(compName) if " "+gram+" " in " "+headline+" "]
    if len(matchedComp) == 0:
        return None
    matchScore = [round(len(gram.split())*1.0/len(compName.split()), 2) for gram, compName in matchedComp]
    fullMatch = [matchedComp[idx] for idx in range(len(matchedComp)) if matchScore[idx] >= 0.8]
    if len(fullMatch) < 1: return None
    #print fullMatch
    if len(fullMatch) > 1:
        match_unique = {}
        for item in fullMatch:
            if item[1] in match_unique:
                if len(item[0]) > len(match_unique[item[1]]):
                    match_unique[item[1]] = item[0]
            else:
                match_unique[item[1]] = item[0]
        fullMatch = [(item[1], item[0]) for item in match_unique.items()]
    return fullMatch


def compInDoc(docText, snp_comp, symCompHash, filtLong, nameOnly):
    comps_name = findComp_name(docText, snp_comp)

    if nameOnly:
        comps = comps_name
    else:
        comps = [(word, symCompHash[word[1:]]) for word in docText.split() if word[0]=='$' and word[1:] in symCompHash]
        if comps_name is not None:
            comps.extend(comps_name)

    if filtLong and len(comps) > 4:
        #print "** Long comps", comps
        return None
    return comps


def evalTClusters(tweetClusters, textNewsDay, newsSeqCompDay, snp_comp, symCompHash, outputDetail):
    trueCluster = []
    matchedNews = []

    #print "--News comps", [newsCompItem[0] for newsIdx, newsComps in enumerate(newsSeqCompDay) for newsCompItem in newsComps]
    for outIdx, cluster in enumerate(tweetClusters):
        clabel, cscore, segments = cluster
        textsIn = " ".join(segments)
        compsIn = compInDoc(textsIn, snp_comp, symCompHash, False, False)

        newsMatchComp = [newsIdx for comp in compsIn for newsIdx, newsComps in enumerate(newsSeqCompDay) for newsCompItem in newsComps if comp[1] == newsCompItem[0]]
        matchedNews_c = tClusterMatchNews_content(newsSeqCompDay, textNewsDay, textsIn, compsIn)

        if outputDetail:
            print "############################"
            print "1-** cluster", outIdx, clabel, cscore, compsIn
            print segments

        if matchedNews_c is None: continue

        trueCluster.append((outIdx, matchedNews_c))
        matchedNews.extend(matchedNews_c)

        if outputDetail:
            #sortedNews = sorted(simToNews_byComp, key = lambda a:a[1], reverse = True)
            sortedNews = Counter(matchedNews_c).most_common()
            for idx, sim in sortedNews:
                print '-MNews', idx, sim, textNewsDay[idx]

    matchedNews = Counter(matchedNews)
    if 1:
        print "TrueClusters", trueCluster
        matchNewsDetails = {}
        for cid, nids in trueCluster:
            for nid in set(nids): 
                if nid in matchNewsDetails:
                    matchNewsDetails[nid].append(cid)
                else:
                    matchNewsDetails[nid] = [cid]
        print "MCNewsDetail", sorted(matchNewsDetails.items(), key = lambda a:a[0])
    return len(trueCluster), len(matchedNews)


def outputEval(Nums):
    print "## Eval newsMatchedCluster", sum(Nums[0]), sum(Nums[1]), round(float(sum(Nums[0])*100)/sum(Nums[1]), 2)
    print "## Eval sysMatchedNews", sum(Nums[2]), sum(Nums[3]), round(float(sum(Nums[2])*100)/sum(Nums[3]), 2)

def outputEval_day(Nums):
    print "## newsPre", Nums[0][-1], Nums[1][-1], ("%.2f" %(Nums[0][-1]*100.0/Nums[1][-1])), "\t",
    print "## newsRecall", Nums[2][-1], Nums[3][-1], "\t", round(float(Nums[2][-1]*100)/Nums[3][-1], 2)

def evalOutputEvents(dayClusters, Para_newsDayWindow, newsSeqDayHash, vecNews, dayNews, newsSeqComp, snp_comp, symCompHash):

    topK_c = 30
    Kc_step = 1 #topK_c
    outputDetail = False
    for sub_topK_c in range(Kc_step, topK_c+1, Kc_step):
        dev_Nums = [[], [], [], []] # trueCNums, cNums, matchNNums, nNums 
        if sub_topK_c == topK_c: outputDetail = True
        for cItem in dayClusters:
            day, tweetClusters = cItem

            sub_tweetClusters = tweetClusters[:min(sub_topK_c, len(tweetClusters))]
            newsDayWindow = [int(day)+num for num in Para_newsDayWindow]
            vecNewsDay, textNewsDay, newsSeqCompDay = dayNewsExtr(newsDayWindow, newsSeqDayHash, vecNews, dayNews, newsSeqComp)

            if 0:
                print "## News in day", day
                for item in textNewsDay:
                    print item
            if outputDetail:
                print "## Output details of Clusters in day", day

            trueCNum, matchNNum = evalTClusters(sub_tweetClusters, textNewsDay, newsSeqCompDay, snp_comp, symCompHash, outputDetail)

            dev_Nums[0].append(trueCNum)
            dev_Nums[1].append(len(sub_tweetClusters))
            dev_Nums[2].append(matchNNum)
            dev_Nums[3].append(len(textNewsDay))
            if trueCNum > 0:
                outputEval_day(dev_Nums)
        ##############

        ##############
        # output evaluation metrics_recall
        if sum(dev_Nums[1]) > 0:
            print "** Dev exp in topK_c", sub_topK_c
            outputEval(dev_Nums)
        ##############


stock_newsDir = '/home/yanxia/SED/ni_data/stocknews/'
snpFilePath = "/home/yanxia/SED/data/snp500_sutd"
newsVecPath = "/home/yanxia/SED/ni_data/tweetVec/stockNewsVec1_Loose1"
dataFilePath = r"/home/yanxia/SED/ni_data/word/"

###############################################################
if __name__ == "__main__":
    Para_newsDayWindow = [0]#[-1, 0, 1]
    devDays = ['06', '07', '08']
    testDays = ['11', '12', '13', '14', '15']
    kNeib = 9
    taoRatio = 2

    #[(day, [(clabel, cscore, segments)])]
    dayOutClusters = []
    for tStr in testDays:
        clusters = []
        structEventFile = file(dataFilePath + "StructEventFile" + tStr + "_k" + str(kNeib) + "t" + str(taoRatio), "r")
        validEventHash = cPickle.load(structEventFile)
        filteredEventHash = cPickle.load(structEventFile)
        reverseSegHash = cPickle.load(structEventFile)

        sortedEventlist = sorted(validEventHash.items(), key = lambda a:a[1])
        for eventItem in sortedEventlist:
            eventId = eventItem[0]
            event = filteredEventHash[eventId]
            nodeList = event.nodeHash.keys()
            segments = [reverseSegHash[id] for id in nodeList]
            clusters.append((eventId, eventItem[1], segments))

        dayOutClusters.append((tStr, clusters))

    ##############
    sym_names = snpLoader.loadSnP500(snpFilePath)
    snp_syms = [snpItem[0] for snpItem in sym_names]
    snp_comp = [strUtil.getMainComp(snpItem[1]) for snpItem in sym_names]
    symCompHash = dict(zip(snp_syms, snp_comp))
    ##############

    ##############
    # load news vec
    newsVecFile = open(newsVecPath, "r")
    print "## news obtained for eval", newsVecPath 
    dayNews = cPickle.load(newsVecFile)
    vecNews = cPickle.load(newsVecFile)
    newsSeqDayHash = cPickle.load(newsVecFile)
    newsSeqComp = cPickle.load(newsVecFile)
   ##############

    evalOutputEvents(dayOutClusters, Para_newsDayWindow, newsSeqDayHash, vecNews, dayNews, newsSeqComp, snp_comp, symCompHash)
    print "Program ends at ", time.asctime()
