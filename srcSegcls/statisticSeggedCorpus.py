#! /usr/bin/env python
#coding=utf-8
import time
import re
import os

print "###program starts at " + str(time.asctime())
#dataFilePath = r"../Data_hfmon/segged/"
dataFilePath = r"../Data_hfmon/segged_ltwe/"
fileList = os.listdir(dataFilePath)
wordHash = {} #word:apphash
#apphash --> tweetIDStr:1
windowHash = {} # timeSliceIdStr:tweetNum
dfFile = file(dataFilePath + "word_df", "w")
fileList = sorted(fileList)
wordNumList = []
segNumList = []
wordRatioList = []
segRatioList = []
for item in fileList:
    if item.find("segged") != 0:
        continue
    seggedFile = file(dataFilePath + item)
    print "### Processing " + seggedFile.name
    tStr = item[len(item)-2:len(item)]
    print "Time window: " + tStr
    tweetNum_t = 0
    word_t_Hash = {}
    segment_t_Hash = {}
    while True:
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
            for word in wordArr:
                apphash = {}
                if word in wordHash:
                    apphash = wordHash[word]
                apphash[tweetIDstr] = 1
                wordHash[word] = apphash 

                # statistic word information in current time window
                app_t_hash = {}
                if word in word_t_Hash:
                    app_t_hash = word_t_Hash[word]
                if tweetIDstr in app_t_hash:
                    app_t_hash[tweetIDstr] += 1
                else:
                    app_t_hash[tweetIDstr] = 1
                word_t_Hash[word] = app_t_hash 

            # statistic segemnt information in current time window
            segApphash = {}
            if segment in segment_t_Hash:
                segApphash = segment_t_Hash[segment]
            if tweetIDstr in segApphash:
                segApphash[tweetIDstr] += 1
            else:
                segApphash[tweetIDstr] = 1
            segment_t_Hash[segment] = segApphash
#        if tweetNum_t % 1000000 == 0:
#            print "### " + str(time.asctime()) + " " + str(tweetNum_t) + " tweets are processed!"
    windowHash[tStr] = tweetNum_t
    seggedFile.close()
    print "### " + str(time.asctime()) + " words in " + item + " are loaded."
    
    ## output each days statistical information
    print "######### statistic information of twitter data on Jan" + tStr
    print "wordNum: " + str(len(word_t_Hash)) + " segmentNum: " + str(len(segment_t_Hash))
    print "Ratio word: " + str(round(len(word_t_Hash)*100.0/tweetNum_t,2)) + " segment: " + str(round(len(segment_t_Hash)*100.0/tweetNum_t,2))
    wordNumList.append(str(len(word_t_Hash)))
    segNumList.append(str(len(segment_t_Hash)))
    wordRatioList.append(str(round(len(word_t_Hash)*100.0/tweetNum_t, 2)))
    segRatioList.append(str(round(len(segment_t_Hash)*100.0/tweetNum_t, 2)))
    wordTFDistribution = {}
    wordDFDistribution = {}
    segmentTFDistribution = {}
    segmentDFDistribution = {}
    maxTFWord = 0
    maxDFWord = 0
    maxTFSeg = 0
    maxDFSeg = 0
    for word in word_t_Hash:
        app_t_hash = word_t_Hash[word]
        df = len(app_t_hash)
        tf = sum(app_t_hash.values())
        if tf > maxTFWord:
            maxTFWord = tf
        if df > maxDFWord:
            maxDFWord = df
        if tf in wordTFDistribution:
            wordTFDistribution[tf] += 1
        else:
            wordTFDistribution[tf] = 1
        if df in wordDFDistribution:
            wordDFDistribution[df] += 1
        else:
            wordDFDistribution[df] = 1
    print "## word tf distribution(by tf): "
    moreThanTFWord = dict([(pow(10, i), 0) for i in range(0, len(str(maxTFWord)))])
    moreThanTFWord[0] = 0
    for item in sorted(wordTFDistribution.items(), key = lambda a:a[0], reverse = True):
        for tf in moreThanTFWord:
            if item[0] > tf:
                moreThanTFWord[tf] += item[1]
    for item in sorted(moreThanTFWord.items(), key = lambda a:a[0], reverse = True):
        val = str(item[1])
        if item[1] > 100:
            val = str(round(item[1]*100.0/len(word_t_Hash),2)) + "%"
        print "(" + str(item[0]) + "," + val + "), ",
    print "\n## word tf distribution(by word numbers): "
    for item in sorted(wordTFDistribution.items(), key = lambda a:a[1], reverse = True)[0:50]:
        val = str(item[1])
        if item[1] > 100:
            val = str(round(item[1]*100.0/len(word_t_Hash),2)) + "%"
        print "(" + str(item[0]) + "," + val + "), ",
    print "\n## word df distribution(by df): "
    moreThanDFWord = dict([(pow(10, i), 0) for i in range(0, len(str(maxDFWord)))])
    moreThanDFWord [0] = 0
    for item in sorted(wordDFDistribution.items(), key = lambda a:a[0], reverse = True):
        for df in moreThanDFWord:
            if item[0] > df:
                moreThanDFWord[df] += item[1]
    for item in sorted(moreThanDFWord.items(), key = lambda a:a[0], reverse = True):
        val = str(item[1])
        if item[1] > 100:
            val = str(round(item[1]*100.0/len(word_t_Hash),2)) + "%"
        print "(" + str(item[0]) + "," + val + "), ",
    print "\n## word df distribution(by word numbers): "
    for item in sorted(wordDFDistribution.items(), key = lambda a:a[1], reverse = True)[0:50]:
        val = str(item[1])
        if item[1] > 100:
            val = str(round(item[1]*100.0/len(word_t_Hash),2)) + "%"
        print "(" + str(item[0]) + "," + val + "), ",
    print ""
    for segment in segment_t_Hash:
        length = len(segment.split(" "))
        app_t_hash = segment_t_Hash[segment]
        df = len(app_t_hash)
        tf = sum(app_t_hash.values())
        if tf > maxTFSeg:
            maxTFSeg = tf
        if df > maxDFSeg:
            maxDFSeg = df
        lenDis = {}
        if tf in segmentTFDistribution:
            lenDis = segmentTFDistribution[tf]
        if length in lenDis:
            lenDis[length] += 1
        else:
            lenDis[length] = 1
        segmentTFDistribution[tf] = lenDis
        lenDFDis = {}
        if df in segmentDFDistribution:
            lenDFDis = segmentDFDistribution[df]
        if length in lenDFDis:
            lenDFDis[length] += 1
        else:
            lenDFDis[length] = 1
        segmentDFDistribution[df] = lenDFDis
    print "## segment tf distribution(by tf): "
    moreThanTFSeg = dict([(pow(10, i), 0) for i in range(0, len(str(maxTFSeg)))])
    moreThanTFSeg[0] = 0
    for item in sorted(segmentTFDistribution.items(), key = lambda a:a[0], reverse = True)[0:100]:
        tf = item[0]
        lenDis = item[1]
        segmentNum = sum(lenDis.values())
        for tf in moreThanTFSeg:
            if item[0] > tf:
                moreThanTFSeg[tf] += segmentNum
#        print "tf: " + str(tf) + " segNum: " + str(segmentNum) + " length distribution: ",
#        print sorted(lenDis.items(), key = lambda a:a[1], reverse = True)
    for item in sorted(moreThanTFSeg.items(), key = lambda a:a[0], reverse = True):
        val = str(item[1])
        if item[1] > 100:
            val = str(round(item[1]*100.0/len(word_t_Hash),2)) + "%"
        print "(" + str(item[0]) + "," + val + "), ",
    print "\n## segment df distribution(by df): "
    moreThanDFSeg = dict([(pow(10, i), 0) for i in range(0, len(str(maxDFSeg)))])
    moreThanDFSeg[0] = 0
    for item in sorted(segmentDFDistribution.items(), key = lambda a:a[0], reverse = True):
        df = item[0]
        lenDis = item[1]
        segmentNum = sum(lenDis.values())
        for df in moreThanDFSeg:
            if item[0] > df:
                moreThanDFSeg[df] += segmentNum
#        print "df: " + str(df) + " segNum: " + str(segmentNum) + " length distribution: ",
#        print sorted(lenDis.items(), key = lambda a:a[1], reverse = True)
    for item in sorted(moreThanDFSeg.items(), key = lambda a:a[0], reverse = True):
        val = str(item[1])
        if item[1] > 100:
            val = str(round(item[1]*100.0/len(word_t_Hash),2)) + "%"
        print "(" + str(item[0]) + "," + val + "), ",
    print ""
print "### " + str(len(wordHash)) + " words in " + dataFilePath + "  are loaded at " + str(time.asctime())

# write each day's tweetNumber into first line
# Format:01 num1#02 num2#...#15 num15
sortedTweetNumList = sorted(windowHash.items(), key = lambda a:a[0])
tweetNumStr = ""
for item in sortedTweetNumList:
    tStr = item[0]
    tweetNum = item[1]
    tweetNumStr += tStr + " " + str(tweetNum) + "#"
dfFile.write(tweetNumStr[:-1] + "\n")
print "### tweets Num in each time window: "
print sortedTweetNumList 

print "wordNumList: " + str(wordNumList)
print "\t".join(wordNumList)
print "wordRatioList: " + str(wordRatioList)
print "\t".join(wordRatioList)
print "segNumList: " + str(segNumList)
print "\t".join(segNumList)
print "segRatioList: " + str(segRatioList)
print "\t".join(segRatioList)
itemNum = 0
for word in sorted(wordHash.keys()):
    itemNum += 1
    apphash = wordHash[word]
    df = len(apphash)
    dfFile.write(str(df) + "\t" + word + "\n")
#    if itemNum % 1000000 == 0:
#        print "### " + str(itemNum) + " words' df values are processed at " + str(time.asctime())

print "### words' df values are written to " + dfFile.name
dfFile.close()
print "###program ends at " + str(time.asctime())
