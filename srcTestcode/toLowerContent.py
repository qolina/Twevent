#! /usr/bin/env python
#coding=utf-8
import time
import re
import os

dataFilePath = r"../tools/"
fileList = os.listdir(dataFilePath)
for item in fileList:
    subFile = file(dataFilePath + item)
    newFile = file(dataFilePath + item + "_lower", "w")
    gramHash = {}
    while True:
        lineStr = subFile.readline()
        lineStr = re.sub(r'\n', " ", lineStr)
        lineStr = re.sub(r'\s+', " ", lineStr)
        lineStr = lineStr.strip()
        if len(lineStr) <= 0:
            break
        prob = lineStr[0:lineStr.find(" ")]
        gram = lineStr[lineStr.find(" ")+1:len(lineStr)]
        gram = gram.lower()
        gramHash[gram] = prob
#        print lineStr
#        print gram + "#\t" + str(prob)
        if len(gramHash)%10000 == 0:
            print str(len(gramHash)) + " grams are processed!"
    for item in gramHash.keys():
        newFile.write(str(gramHash[item]) + "\t" + item + "\n")
#        print str(gramHash[item]) + " " + item
    subFile.close()
    newFile.close()
    print "### " + str(time.asctime()) + " #" + str(len(gramHash)) + " grams are loaded."
