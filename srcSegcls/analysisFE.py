#! /usr/bin/env python
#coding=utf-8
import time
import re
import os

print "###program starts at " + str(time.asctime())
dataFilePath = "../segged_hfmon/labelledEvents_postprocess/"
feventFile = file(dataFilePath + "l_falseEventList")
separateFEFile = file(dataFilePath + "l_falseEvent_arranged", "w")
eventDesHash = {}
eventId = 0
while True:
    lineStr = feventFile.readline()
    lineStr = re.sub(r'\n', " ", lineStr)
    lineStr = lineStr.strip()
    if len(lineStr) <= 0:
        break
    if lineStr.startswith("###"):
        eventId += 1
        arr = lineStr.split("###")
        eventClass = arr[1]
        eventDesStr = ""
        if eventClass in eventDesHash:
            eventDesStr = eventDesHash[eventClass]
        eventDesStr += lineStr
        nextLine = feventFile.readline()
        eventDesStr += "\n" + nextLine
        eventDesHash[eventClass] = eventDesStr
feventFile.close()
print "Event Num: " + str(eventId)
print "Event Class Num: " + str(len(eventDesHash))
print eventDesHash.keys()
for eventClass in sorted(eventDesHash.keys()):
    eventDesStr = eventDesHash[eventClass]
    separateFEFile.write(eventDesStr)
separateFEFile.close()
print "###program ends at " + str(time.asctime())
