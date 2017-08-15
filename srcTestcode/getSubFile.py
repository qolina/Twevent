#! /usr/bin/env python
#coding=utf-8
import time
import re
import os

dataFilePath = r"../tools/"
fileList = []
for i in range(1,6):
    item = "ngrams_gram" + str(i)
    fileList.append(item)
print fileList

for item in fileList:
    gramFile = file(dataFilePath + item)
    probFile = file(dataFilePath + item + "_prob_lower")
    newFile = file(dataFilePath + item + "_prob", "w")
    gramHash = {}
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
        lineStr = re.sub(r'\s+', " ", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        prob = lineStr[0:lineStr.find("\t")]
        gram = lineStr[lineStr.find("\t")+1:len(lineStr)]
        
        if gram in gramHash:
            print str(prob) + "\t" + gram
            newFile.write(str(prob) + "\t" + gram + "\n")
    gramFile.close()
    probFile.close()
    newFile.close()
    print "### " + str(time.asctime()) + " #" + str(len(gramHash)) + " grams are loaded."
