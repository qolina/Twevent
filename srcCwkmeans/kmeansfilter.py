
import os
import random
import math
import time
import sys

def loadDataArff(dataPath):
    datalist = []
    FeaNum = 0
    inputlabellist = []
    dataFile = file(dataPath)
    contentArr = dataFile.readlines()
    lineIdx = 0
    while lineIdx < len(contentArr):
        lineStr = contentArr[lineIdx]
        if lineStr.startswith("@data"):
            for i in range(lineIdx+1, len(contentArr)):
                dataStr = contentArr[i][:-1]
                dataArr = dataStr.split(",")

                ## manually assigned label
                if dataArr[len(dataArr)-1] == "1":
                    inputlabellist.append(1)
                else:
                    inputlabellist.append(0)

                ## data's feature vector
                arr = list([float(val) for val in dataArr[:-1]])
                datalist.append(arr)
            break
        else:
            lineIdx += 1

    FeaNum = len(datalist[0])
    print "### Loading ends. " + str(time.asctime()) + " " + str(len(datalist)) + " items and " + str(FeaNum) + " features in each item are from " + dataPath
    return datalist, FeaNum, inputlabellist

def loadDataLibsvm(dataPath):
    datalist = []
    FeaNum = 0
    inputlabellist = []
    dataFile = file(dataPath)
    contentArr = dataFile.readlines()
    for dataStr in contentArr:
        dataStr = dataStr[:-1]
        dataArr = dataStr.split(" ")

        ## manually assigned label
        if len(dataArr[0]) == 1:
            inputlabellist.append(labelMap1[dataArr[0]]) 
        else:
            inputlabellist.append(labelMap2[dataArr[0]]) 

        ## data's feature vector
        arr = list([float(val[val.find(":")+1:]) for val in dataArr[1:]])
        datalist.append(arr)
    FeaNum = len(datalist[0])
    print "### Loading ends. " + str(time.asctime()) + " " + str(len(datalist)) + " items and " + str(FeaNum) + " features in each item are from " + dataPath
    return datalist, FeaNum, inputlabellist

def EuclideanDistance(vec1, vec2):
    if len(vec1) != len(vec2):
        print "Error in Euclidean distance. Not equal length vector"
        return 0.0
    dis = 0.0
    sqrSum = 0.0
    sqrSum = sum([(vec1[i]-vec2[i])*(vec1[i]-vec2[i]) for i in range(len(vec1))])
#    for i in range(len(vec1)):
#        sqrSum += (vec1[i] - vec2[i])*(vec1[i] - vec2[i])
    dis = math.sqrt(sqrSum)
    return dis

def initializeManual(centroidlist):
    if len(centroidlist) != k:
        print "Error in k-means initialize Manual! Data point number != k"
    centroidHash = {}
    for i in range(0, len(centroidlist)):
        centroidHash[i] = datalist[centroidlist[i]]
    print "# Manually select seed: " + str(centroidlist)
    return centroidHash

def initializeRandom():
    centroidHash = {}
    usedNo = []
    centroidlist = random.sample(range(0, len(datalist)), k)
    print "# Randomly select seed: " + str(centroidlist)
    for i in range(0, len(centroidlist)):
        centroidHash[i] = datalist[centroidlist[i]]
    return centroidHash

def avgData(dataInside, FeaNum):
    centroid = [0.0 for i in range(FeaNum)]
    for data in dataInside:
        for i in range(FeaNum):
            centroid[i] += data[i]
    for i in range(FeaNum):
        centroid[i] = centroid[i] / len(dataInside)
    return centroid

def kMeans(manualFlag):
    if manualFlag:
        # manually assign seed data
        centroidlist = [3,32]
        centroidHash = initializeManual(centroidlist)
    else:
        # randomly choose k seed data
        centroidHash = initializeRandom()
    
    iterId = 0
    labellist = [-1 for i in range(len(datalist))]
    preLabellist = [-1 for i in range(len(datalist))]
    stable = False

    preJ = 10**10 
    J = preJ - 10.0
#    while preJ - J > minThreshold:
    while not stable:
        print "###Running Iteration: " + str(iterId) + " preJ " + str(preJ) + " J " + str(J) + " diff: " + str(preJ-J)
        iterId += 1
        preJ = J
        J = 0.0
        ## step1: assign label for data
        stable = True
        for i in range(0, len(datalist)):
            data = datalist[i]
            minDis = 99999
            nearestCentroid = -1
            for j in sorted(centroidHash.keys()):
                centroid = centroidHash[j]
                dis = EuclideanDistance(data, centroid)
                if dis < minDis:
                    minDis = dis
                    nearestCentroid = j
            labellist[i] = nearestCentroid
            if labellist[i] != preLabellist[i]:
                stable = False
                preLabellist[i] = labellist[i]
            J += minDis

        ## step2: recalculate centroids
        newCentroidHash = {}
        for i in range(0, len(datalist)):
            data = datalist[i]
            label = labellist[i]
            dataInside = []
            if label in newCentroidHash:
                dataInside = newCentroidHash[label]
            dataInside.append(data)
            newCentroidHash[label] = dataInside
        for j in sorted(newCentroidHash.keys()):
            dataInside = newCentroidHash[j]
            centroid = avgData(dataInside, FeaNum)
            centroidHash[j] = centroid

    print "### " + str(time.asctime()) + " clustering ends. Iteration " + str(iterId) + " preJ " + str(preJ) + " J " + str(J) + " diff " + str(preJ - J)

    return labellist, centroidHash

def toPositiveSet(num):
    bnum = bin(num)
    bStr = bnum[2:]
    if len(bStr) < 12:
        bStr = bStr.zfill(12)
    positiveSet = []
    for i in range(1, 13):
        if bStr[i-1] == "1":
            if (i == 11) | (i == 12):
                positiveSet.append(i+1)
            else:
                positiveSet.append(i)
    return positiveSet

def outputResult(predictfilename):
    predictFile = file(predictfilename, "w")
    centroidNumHash = {}
    for i in range(len(datalist)):
        data = datalist[i]
        label = labellist[i]
        # instance number in cluster
        dataNumInside = []
        if label in centroidNumHash:
            dataNumInside = centroidNumHash[label]
        dataNumInside.append(i)
        centroidNumHash[label] = dataNumInside
    for j in sorted(centroidNumHash.keys()):
        dataNumInside = centroidNumHash[j]
        print "Cluster " + str(j) + ", inst num: " + str(len(dataNumInside))

    ###### evaluation of k-means clustering
    ## assign manual label to clusters
    [eventLabel, stNum] = determineByError(centroidNumHash)
#    [eventLabel, stNum] = determinBydis()

    ## calculate precision, recall and f1
    mtNum = sum(trueLabellist)
    sNum = len(centroidNumHash[eventLabel])
    [pr, r, f1] = getMetric(stNum, sNum, mtNum)
    print "### kmeans test: P: " + str(pr) + " R: " + str(r) + " F1: " + str(f1),
    print " stNum: " + str(stNum) + " sNum: " + str(sNum) + " mtNum: " + str(mtNum)
    if pr >= 0.5:
        print "### Successful weight!"
#    sPosSet = getPositiveSet(sysCentroidHash, eventLabel)
#    print "#Extra resource: system positive set: " + str(sPosSet)
    for i in range(len(datalist)):
        data = datalist[i]
        label = labellist[i]
        toCWlabelStr = toCWlabelMap[label]
        dataNew = [str(i+1)+":"+str(data[i]) for i in range(len(data))]
        predictFile.write(toCWlabelStr + " " + " ".join(dataNew) + "\n")
    predictFile.close() 

def determineByError(centroidNumHash):
    ## num of datum in different mapping pattern
    dnum = {"s0m0":0, "s0m1":0, "s1m0":0, "s1m1":0}
    error = {"s0m1":0, "s1m1":0}
    for lb in range(0, k):
        for dataID in centroidNumHash[lb]:
            mlb = trueLabellist[dataID]
            idstr = "s"+str(lb) + "m"+str(mlb)
            dnum[idstr] += 1
    error["s1m1"] = dnum["s0m1"]+dnum["s1m0"]
    error["s0m1"] = dnum["s0m0"]+dnum["s1m1"]
    eventLabel = 1
    if error["s1m1"] > error["s0m1"]:
        eventLabel = 0
    eventIdStr = "s"+str(eventLabel) + "m1"
    print "### Cluster " + str(eventLabel) + " is the event cluster. Error " + str(error[eventIdStr])
    print "### confusion matrix: \n" + str(dnum["s0m0"]) + "   " + str(dnum["s1m0"]) + "\n" + str(dnum["s0m1"]) + "   " + str(dnum["s1m1"])
    stNum = dnum[eventIdStr]
    return eventLabel, stNum

def determinBydis():
    dis_s0_m0 = EuclideanDistance(sysCentroidHash[0], manualCentroid[0])
    dis_s0_m1 = EuclideanDistance(sysCentroidHash[0], manualCentroid[1])
    dis_s1_m0 = EuclideanDistance(sysCentroidHash[1], manualCentroid[0])
    dis_s1_m1 = EuclideanDistance(sysCentroidHash[1], manualCentroid[1])
    print str(dis_s0_m1) + " " + str(dis_s1_m1)
    print str(dis_s0_m0) + " " + str(dis_s1_m0)

    if (dis_s0_m1 < dis_s1_m1):
        if (dis_s0_m0 > dis_s1_m0):
            eventLabel = 0
            print "event label: 0 (msg: perfect)"
        else:
            if (dis_s0_m0 > dis_s0_m1):
                eventLabel = 0
                print "event label: 0 (msg: both close to 0, closer)"
                print "event label: 0 (msg: both close to 0, further)"
    else:
        if (dis_s0_m0 < dis_s1_m0):
            print "event label: 1 (msg: perfect)"
        else:
            if (dis_s1_m0 > dis_s1_m1):
                print "event label: 1 (msg: both close to 1, closer)"
            else:
                print "event label: 1 (msg: both close to 1, further)"
    return eventLabel

def getManualCentroid():
    centroids = {}
    centroidHash = {}
    for i in range(len(datalist)):
        data = datalist[i]
        label = trueLabellist[i]
        dataInside = []
        if label in centroidHash:
            dataInside = centroidHash[label]
        dataInside.append(data)
        centroidHash[label] = dataInside
    for j in sorted(centroidHash.keys()):
        dataInside = centroidHash[j]
        centroid = avgData(dataInside, FeaNum)
        centroids[j] = centroid
#        print "manual cluster " + str(j) + ": " + str(centroid)

    mPosSet = getPositiveSet(centroids, 1) 
#    print "#Extra resource: manual positive set: " + str(mPosSet)
    return centroids

def getMetric(stNum, sNum, mtNum):
    pr = 0.0
    r = 0.0
    f1 = 0.0
    if stNum > 0:
        pr = stNum*1.0/sNum
        r = stNum*1.0/mtNum
        f1 = 2*pr*r/(pr+r)
    return round(pr, 4), round(r, 4), round(f1, 4)

def getPositiveSet(centroidHash, eventLabel):
    ## get extra resource
    sPosSet = []
    for i in range(1, 14):
        if centroidHash[eventLabel][i] > centroidHash[1-eventLabel][i]:
            sPosSet.append(i)
    return sPosSet

def loadTrueLabel(truelabelfilename):
    lFile = file(truelabelfilename)
    contentArr = lFile.readlines()
    inputlabellist = [int(lineStr[0]) for lineStr in contentArr if len(lineStr)>0]
    lFile.close()
    return inputlabellist
    
# get parameters
def getparameter():
    suffix = ""
    inputfilename = ""
    predictfilename = ""
    truelabelfilename = ""
    manualFlag = False
    if len(sys.argv) == 1:
        print "Usage: kmeansfilter.py [-p pnum -m -s suffixStrForFile] -if inputfilename -of predictfilename -tl truelabelfilename"
        sys.exit()
    if "-p" in sys.argv:
        pnum = sys.argv[sys.argv.index("-p")+1]
        print "###PositiveSet: " + str(toPositiveSet(int(pnum))) + " " + num
    if "-s" in sys.argv:
        suffix += "_" + sys.argv[sys.argv.index("-s")+1]
    if "-m" in sys.argv:
        manualFlag = True
    if "-if" in sys.argv:
        inputfilename = sys.argv[sys.argv.index("-if")+1]
    if "-of" in sys.argv:
        predictfilename = sys.argv[sys.argv.index("-of")+1]
    if "-tl" in sys.argv:
        truelabelfilename = sys.argv[sys.argv.index("-tl")+1]
    return suffix, manualFlag, inputfilename, predictfilename, truelabelfilename

#####################################################################
## main function
print "### " + str(time.asctime()) + " k-means filter program starts."
global datalist, FeaNum, k, minThreshold, labellist, trueLabellist, manualCentroid, sysCentroidHash
k = 2
#minThreshold = math.pow(0.1, 10)
dirPath = r"../Data_hfmon/segged_ltwe/classify/"
#dataPath = dirPath + "EventDataset_All.libsvm"
print sys.argv
[suffix, manualFlag, inputfilename, predictfilename, truelabelfilename] = getparameter()
global labelMap1, labelMap2, toCWlabelMap
labelMap1 = {"1":1, "0":0}
labelMap2 = {"+1":1, "-1":0}
toCWlabelMap = {1:"+1", 0:"-1"}
#dataPath = dirPath + r"EventDataset_All" + suffix + ".libsvm"
#dataPath = dirPath + r"EventDataset_All" + suffix + ".libsvm.binary"
print "====Loading===="
[datalist, FeaNum, inputlabellist] = loadDataLibsvm(inputfilename)
if False:
    inputlabelStrlist = [str(lb) for lb in inputlabellist]
    labelfile = file("trueLabel.txt", "w")
    labelfile.write("\n".join(inputlabelStrlist))
    print "### True label file is generated: " + labelfile.name
    labelfile.close()
#if len(truelabelfilename) == 0:
if "-tl" not in sys.argv:
    trueLabellist = list([val for val in inputlabellist]) #v1
    print "### Num of positive inst in input labelSet: " + str(sum(trueLabellist))
else:
    trueLabellist = loadTrueLabel(truelabelfilename)
    print "### Manually labeled labelSet is loaded! with " + str(sum(trueLabellist)) + " positive inst."

print "====Clustering===="
manualCentroid = getManualCentroid()
[labellist, sysCentroidHash] = kMeans(manualFlag)

print "====Evaluation===="
outputResult(predictfilename)
print "### predict file: " + predictfilename
print "### " + str(time.asctime()) + " program ends."
