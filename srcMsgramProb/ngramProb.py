#! /usr/bin/env python
#coding=utf-8

import urllib
import urllib2
import os
import re
import time
import sys

## main
print "Program starts at time:" + str(time.asctime())

#dirPath = r"/home/lavender1c/yxqin/twevent/msgram/grams_hfmon_qtwe/"
dirPath = r"/home/yanxia/SED/ni_data/word/grams/"

args = sys.argv
subFile = file(dirPath + args[1])
probFile = file(dirPath + args[1] + "_prob", "w")
print "## Reading file " + subFile.name
phraseList = []
phrasesStr = ""
emptyGramList = []
lineIdx = 0
while True:
    lineStr = subFile.readline()
    lineStr = re.sub(r'\n', " ", lineStr)
    lineStr = lineStr.strip()
    if len(lineStr) <= 0:
        print str(lineIdx) + " lines are processed."
        break
#    gramStr = re.sub(r'_', " ", lineStr)
#    gramStr = re.sub(r'\s+', " ", gramStr)
    gramStr = re.sub(r'[_]+', "_", lineStr)
    gramStr = gramStr.strip("_")
    if len(gramStr) <= 0:
        print "##Empty gram: " + lineStr
        emptyGramList.append(lineStr)
        continue
    phraseList.append(gramStr)
#    gramStr = urllib.quote(gramStr)
    phrasesStr += gramStr + "\n"
    if len(phraseList) == 1000:
        probStr = urllib2.urlopen(urllib2.Request('http://web-ngram.research.microsoft.com/rest/lookup.svc/bing-body/jun09/3/jp?u=7bb8364a-2d07-4c68-b3c0-c826440a772e',phrasesStr)).read()
        probArr = probStr.split("\r\n")
        for i in range(0, len(phraseList)):
            prob = probArr[i]
            gram = phraseList[i]
            probFile.write(prob + " " + gram + "\n")
        del phraseList[:]
        phrasesStr = ""
    lineIdx += 1
    if lineIdx % 10000 == 0:
        print str(lineIdx) + " lines are processed."
probStr = urllib2.urlopen(urllib2.Request('http://web-ngram.research.microsoft.com/rest/lookup.svc/bing-body/jun09/3/jp?u=7bb8364a-2d07-4c68-b3c0-c826440a772e',phrasesStr)).read()
probArr = probStr.split("\r\n")
for i in range(len(phraseList)):
    prob = probArr[i]
    gram = phraseList[i]
    probFile.write(prob + " " + gram + "\n")
subFile.close()
probFile.close()

print "### " + str(len(emptyGramList)) + " empty grams are detected! ",
print emptyGramList
print "## Probs are written to file " + probFile.name
print "Program ends at time:" + str(time.asctime())

