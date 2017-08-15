#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import math
import cPickle

############################
## load ps from file
def loadslang(slangFilePath):
    global slangHash
    inFile = file(slangFilePath)
    while True:
        lineStr = inFile.readline()
        lineStr = re.sub(r'\n', ' ', lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        contentArr = lineStr.split("  -   ")
        sWord = contentArr[0].strip()
        rWord = contentArr[1].strip()
        slangHash[sWord] = rWord
    inFile.close()
    print "### " + str(len(slangHash)) + " slang words are loaded from " + inFile.name

############################
## load ps from file
def loadps(psFilePath):
    global unitpsHash
    psFile = file(psFilePath)
    while True:
        lineStr = psFile.readline()
        lineStr = re.sub(r'\n', ' ', lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        contentArr = lineStr.split("\t")
        prob = float(contentArr[0])
        unit = contentArr[1]
        unitpsHash[unit] = prob
    psFile.close()
    print "### " + str(len(unitpsHash)) + " " + UNIT + "s' ps values are loaded from " + psFile.name

############################
## load tweetID-usrID
def loadUsrId(filepath):
    usrFile = file(filepath,"r")
    tweIdToUsrIdHash = cPickle.load(usrFile)
    usrFile.close()
    return tweIdToUsrIdHash

############################
## calculate sigmoid
def sigmoid(x):
    return 1.0/(1.0+math.exp(-x))

############################
## getEventSegment
def getEventSegment(dataFilePath, toolDirPath):

    socialFeatureFile = open("/home/yanxia/SED/ni_data/timeCorrect/tweetSocialFeature01", "r")
    socialFeatureHash = cPickle.load(socialFeatureFile)
    socialFeatureFile2 = open("/home/yanxia/SED/ni_data/timeCorrect/tweetSocialFeature02", "r")
    socialFeatureHash2 = cPickle.load(socialFeatureFile2)
    socialFeatureHash.update(socialFeatureHash2)

    stat_segmentHash = {}
    fileList = os.listdir(dataFilePath)
    for item in sorted(fileList):
        if item.find("segged") != 0:
            continue
        print "### Processing " + item
        seggedFile = file(dataFilePath + item)
        tStr = item[len(item)-2:len(item)]
        if tStr not in validDays: continue
        print "Time window: " + tStr
        eventSegFile = file(dataFilePath + "event" + UNIT + tStr, "w")
        N_t = 0
        unitHash = {} #unit:df_t_hash
        #df_t_hash --> tweetIDStr:1
        unitUsrHash = {}
        #tweToUsrFilePath = toolDirPath + "tweIdToUsrId" + tStr
        #tweIdToUsrIdHash = loadUsrId(tweToUsrFilePath)
        
        while True:
            lineStr = seggedFile.readline()
            lineStr = re.sub(r'\n', " ", lineStr)
            lineStr = lineStr.strip()
            if len(lineStr) <= 0:
                break
            contentArr = lineStr.split("\t")
            tweetIDstr = contentArr[0]
            tweetText = contentArr[2]
            #usrIDstr = tweIdToUsrIdHash[tweetIDstr]
            usrIDstr = socialFeatureHash[tweetIDstr]["Usr"]
            if len(tweetText)*len(tweetIDstr) == 0:
                print "Error: empty id or text: " + tweetIDstr + "#" + tweetText
                exit
            N_t += 1
            textArr = tweetText.split("|")
            for segment in textArr:
                wordArr = segment.split(" ")
                containslang = False

                #[GUA] If segment contain word in slang.txt, ignore it.
                # added by qin [refer to TwiNer's postprocess]
                filterSlang = False
                if (filterSlang):
                    for word in wordArr: 
                        if word in slangHash:
                            print "Segment contain slang: #" + word + "# in #" + segment + "#"
                            containslang = True
                            break
                    if containslang:
                        continue

                if useSegmentFlag:
                    #[GUA] SegmentHash mapping: segment -> [twitterID -> 1/0]
                    unit = segment
                    # segment df
                    df_t_hash = {}
                    if unit in unitHash:
                        df_t_hash = unitHash[unit]
                    df_t_hash[tweetIDstr] = 1
                    unitHash[unit] = df_t_hash

                    #[GUA] SegmentUsrHash mapping: segment -> [usrID -> 1/0]
                    # segment users
                    usr_hash = {}
                    if unit in unitUsrHash:
                        usr_hash = unitUsrHash[unit]
                    usr_hash[usrIDstr] = 1
                    unitUsrHash[unit] = usr_hash
                else:
                    for word in wordArr:
                        unit = word
                        # word df
                        df_t_hash = {}
                        if unit in unitHash:
                            df_t_hash = unitHash[unit]
                        df_t_hash[tweetIDstr] = 1
                        unitHash[unit] = df_t_hash

                        # word users
                        usr_hash = {}
                        if unit in unitUsrHash:
                            usr_hash = unitUsrHash[unit]
                        usr_hash[usrIDstr] = 1
                        unitUsrHash[unit] = usr_hash
            if N_t % 100000 == 0:
                print "### " + str(time.asctime()) + " " + str(N_t) + " tweets are processed!"

        #[GUA] WindowHash mapping: timeWindow -> twitterNum
        windowHash[tStr] = N_t
        seggedFile.close()
        print "### " + str(time.asctime()) + " " + UNIT + "s in " + item + " are loaded." + str(len(unitHash))
        if 1:
            stat_segmentHash.update(unitHash)
            continue

        #[GUA] burstySegHash mapping: segment -> wb_st(bursty score)
        burstySegHash = {}
        for unit in unitHash:

            # twitterNum / unit, timeWindow
            f_st = len(unitHash[unit])*1.0

            # usrNum / unit, timeWindow
            u_st_num = len(unitUsrHash[unit])


            #[GUA] segmentpsHash mapping: segment -> ps, N_t: twitterNum / timeWindow
            ps = unitpsHash[unit]
            e_st = N_t * ps
            if f_st <= e_st: # non-bursty segment or word
#                print "### non-bursty " + UNIT + ": " + unit + " f_st: " + str(f_st) + " e_st: " + str(e_st)
                continue
            # bursty segment or word
            sigma_st = math.sqrt(e_st*(1-ps))

            #[GUA] Whether or not f_st in (e_st, e_st + sigma_st) ?

            if f_st >= e_st + 2*sigma_st: # extremely bursty segments or words
                Pb_st = 1.0
            else:
                Pb_st = sigmoid(10*(f_st - e_st - sigma_st)/sigma_st)
            u_st = math.log10(u_st_num)
            wb_st = Pb_st*u_st
#            print "# bursty seg/word: " + unit + " f_st: " + str(f_st) + " e_st: " + str(e_st),
#            print " ps: " + str(ps),
#            print " sigma: " + str(sigma_st),
#            print " pb: " + str(Pb_st),
#            print " u_st: " + str(u_st_num)
#            print " wbScore: " + str(wb_st)
            burstySegHash[unit] = wb_st
        print "Bursty " + UNIT + " num: " + str(len(burstySegHash))
        
        #K = int(math.sqrt(N_t)) + 1
        K = 200
        print "K (num of event " + UNIT + "): " + str(K)
        sortedList = sorted(burstySegHash.items(), key = lambda a:a[1], reverse = True)
        sortedList = sortedList[0:K]
        for key in sortedList:
            eventSeg = key[0]
            f_st = len(unitHash[eventSeg])

            #[GUA] eventSegFile name: eventSeg + TimeWindow, format: f_st(twitterNum / segment, timeWindow), wb_st(bursty score), segment
            eventSegFile.write(str(f_st) + "\t" + str(key[1]) + "\t" + eventSeg + "\n")
        eventSegFile.close()
    print "##Stat: \#segment", len(stat_segmentHash)

############################
## main Function
global useSegmentFlag, UNIT
print "###program starts at " + str(time.asctime())
#dataFilePath = r"../Data_hfmon/segged_ltwe/"
dataFilePath = r"/home/yanxia/SED/ni_data/word/"
# use segment or word as unit
useSegmentFlag = True 
if useSegmentFlag:
    UNIT = "segment"
else:
    UNIT = "word"
psFilePath = dataFilePath + UNIT + "_ps"
slangFilePath = r"../Tools/slang.txt"
toolDirPath = r"../Tools/"
windowHash = {} # timeSliceIdStr:tweetNum
unitpsHash = {} # unit:ps
slangHash = {} #slangword:regular word

devDays = ['06', '07', '08']
testDays = ['11', '12', '13', '14', '15']
global validDays
validDays = testDays #devDays + testDays

loadslang(slangFilePath)
loadps(psFilePath)
getEventSegment(dataFilePath, toolDirPath)

print "###program ends at " + str(time.asctime())
