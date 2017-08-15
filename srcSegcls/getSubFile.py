#! /usr/bin/env python
#coding=utf-8
import time
import re
import os

print "###program starts at " + str(time.asctime())
dataFilePath = r"../Jan01Ngram/"
fileList = []
for i in range(1,6):
    item = "gram" + str(i)
    fileList.append(item)
print fileList

for item in fileList:
    gramFile = file(dataFilePath + "rawGram_" + item)
    probFile = file(dataFilePath + item + "_prob_all")
    newFile = file(dataFilePath + item + "_prob", "w")
    gramHash = {}
    gramProbHash = {}
    while True:
        lineStr = gramFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        lineStr = re.sub(r'\s+', " ", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        gramHash[lineStr] = 1

    while True:
        lineStr = probFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        prob = lineStr[0:lineStr.find(" ")]
        gram = lineStr[lineStr.find(" ")+1:len(lineStr)]
        
        if gram in gramHash:
#            print str(prob) + "\t" + gram
            gramProbHash[gram] = prob
        if len(gramProbHash) == len(gramHash):
            break

    sortedList = sorted(gramProbHash.keys())
    for item in sortedList:
        newFile.write(str(gramProbHash[item]) + " " + item + "\n")
    gramFile.close()
    probFile.close()
    newFile.close()
    print "### " + str(time.asctime()) + " #" + str(len(gramHash)) + " grams are loaded."
print "###program ends at " + str(time.asctime())
