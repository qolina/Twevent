#! /usr/bin/env python
#coding=utf-8
import time
import re
import os
import sys

print "###program starts at " + str(time.asctime())
#dataFilePath = r"../Data_hfmon/segged_qtwe/"
#dataFilePath = r"../Data_hfmon/segged_ltwe/"
#dataFilePath = r"../Data_hfmon/segged_ltwe_hash/"
dataFilePath = r"/home/yanxia/SED/ni_data/word/"
args = sys.argv
useSegmentFlag = False
if args[1] == "seg":
    useSegmentFlag = True
# use segment or word as unit
if useSegmentFlag:
    UNIT = "segment"
else:
    UNIT = "word"
unitHash = {} #unit:df_hash
#df_hash --> timeSliceIdStr:df_t_hash
#df_t_hash --> tweetIDStr:1
unitAppHash = {} #unit:apphash
windowHash = {} # timeSliceIdStr:tweetNum
psFile = file(dataFilePath + UNIT + "_ps", "w")
dfFile = file(dataFilePath + UNIT + "_df", "w")
unitLengthHash = {}
fileList = os.listdir(dataFilePath)
fileList = sorted(fileList)
for item in fileList:
    if item.find("segged") != 0:
        continue
    seggedFile = file(dataFilePath + item)
    print "### Processing " + seggedFile.name
    tStr = item[len(item)-2:len(item)]
    print "Time window: " + tStr
    tweetNum_t = 0
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
        tweetNum_t += 1
        textArr = tweetText.split("|")
        for segment in textArr:
            wordArr = segment.split(" ")
            if useSegmentFlag:
                unit = segment
                # statistic segment df
                apphash = {}
                if unit in unitAppHash:
                    apphash = unitAppHash[unit]
                apphash[tweetIDstr] = 1
                unitAppHash[unit] = apphash 

                # statistic segment ps
                if unit in unitHash:
                    df_hash = unitHash[unit]
                    if tStr in df_hash:
                        df_t_hash = df_hash[tStr]
                    else:
                        df_t_hash = {}
                else:
                    df_hash = {}
                    df_t_hash = {}
                df_t_hash[tweetIDstr] = 1
                df_hash[tStr] = df_t_hash
                unitHash[unit] = df_hash
                wordNum = len(wordArr)
                if unit not in unitLengthHash:
                    unitLengthHash[unit] = wordNum
            else:
                for word in wordArr:
                    unit = word
                    # statistic word df
                    apphash = {}
                    if unit in unitAppHash:
                        apphash = unitAppHash[unit]
                    apphash[tweetIDstr] = 1
                    unitAppHash[unit] = apphash 

                    # statistic word ps
                    if unit in unitHash:
                        df_hash = unitHash[unit]
                        if tStr in df_hash:
                            df_t_hash = df_hash[tStr]
                        else:
                            df_t_hash = {}
                    else:
                        df_hash = {}
                        df_t_hash = {}
                    df_t_hash[tweetIDstr] = 1
                    df_hash[tStr] = df_t_hash
                    unitHash[unit] = df_hash

        if tweetNum_t % 100000 == 0:
            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed!"
    windowHash[tStr] = tweetNum_t
    seggedFile.close()
    print "### " + str(time.asctime()) + " " + UNIT + "s in " + item + " are loaded." + str(len(unitHash))
print "### In total " + str(len(unitHash)) + " " + UNIT + "s are loaded!"

# writing to dffile
# write each day's tweetNumber into first line of df file
# Format:01 num1#02 num2#...#15 num15
sortedTweetNumList = sorted(windowHash.items(), key = lambda a:a[0])
tweetNumStr = ""
for item in sortedTweetNumList:
    tStr = item[0]
    tweetNum = item[1]
    tweetNumStr += tStr + " " + str(tweetNum) + "#"
dfFile.write(tweetNumStr[:-1] + "\n")

itemNum = 0
for unit in sorted(unitAppHash.keys()):
    itemNum += 1
    apphash = unitAppHash[unit]
    df = len(apphash)
    dfFile.write(str(df) + "\t" + unit + "\n")

dfFile.close()
print "### " + UNIT + "s' df values are written to " + dfFile.name

## writing to unit ps file
unitNum = 0
for unit in sorted(unitHash.keys()):
    unitNum += 1
    df_hash = unitHash[unit]
    l = len(df_hash)
    probTemp = 0.0
    for tStr in sorted(df_hash.keys()):
        df_t_hash = df_hash[tStr]
        fst = len(df_t_hash)
        probTemp += (fst*1.0)/windowHash[tStr]
    prob = probTemp/l
    psFile.write(str(prob) + "\t" + unit + "\n")
    if unitNum % 100000 == 0:
        print "### " + str(unitNum) + " units are processed at " + str(time.asctime())

psFile.close()
print "### " + UNIT + "s' ps values are written to " + psFile.name

gramLengDis = []
gram1Num = len(dict([(unit, 1) for unit in unitLengthHash if unitLengthHash[unit] == 1]))
gram2Num = len(dict([(unit, 1) for unit in unitLengthHash if unitLengthHash[unit] == 2]))
gram3Num = len(dict([(unit, 1) for unit in unitLengthHash if unitLengthHash[unit] == 3]))
gram4Num = len(dict([(unit, 1) for unit in unitLengthHash if unitLengthHash[unit] == 4]))
gram5Num = len(unitLengthHash) - gram1Num - gram2Num - gram3Num - gram4Num
gramLengDis.append(gram1Num)
gramLengDis.append(gram2Num)
gramLengDis.append(gram3Num)
gramLengDis.append(gram4Num)
gramLengDis.append(gram5Num)
print "### " + str(len(unitLengthHash)) + " segments' length distribution:",
print gramLengDis

print "###program ends at " + str(time.asctime())
