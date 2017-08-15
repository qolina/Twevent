import os
import random
import math
import time
import sys

# get parameters
def getparameter():
    suffix = ""
    scoreThreshold = 0.0
    feaId = 0
    sumFilterFlag = False
    mlpFilterFlag = False
    normFilterFlag = False
    voteFilterFlag = False
    toChangeFeas = []
    if len(sys.argv) == 1:
        print "Usage: unsupfilter.py [-p pnum -f feaId -norm -sum -vote -c toChangeFeas] -s suffixStr -n scoreThreshold"
        sys.exit()
    if "-p" in sys.argv:
        pnum = sys.argv[sys.argv.index("-p")+1]
        print "###Already used PositiveSet: " + str(toPositiveSet(int(pnum))) + " " + pnum
    if "-s" in sys.argv:
        suffix += "_" + sys.argv[sys.argv.index("-s")+1]
    if "-n" in sys.argv:
        scoreThreshold = float(sys.argv[sys.argv.index("-n")+1])
    if "-f" in sys.argv:
        feaId = int(sys.argv[sys.argv.index("-f")+1])
    if "-sum" in sys.argv:
        sumFilterFlag = True
    if "-mlp" in sys.argv:
        mlpFilterFlag = True
    if "-norm" in sys.argv:
        normFilterFlag = True
    if "-vote" in sys.argv:
        voteFilterFlag = True
    if "-c" in sys.argv:
        toDelFeasStr = sys.argv[sys.argv.index("-c")+1]
        arr = toDelFeasStr.split("_")
        toChangeFeas = list([int(val) for val in arr])
    return suffix, scoreThreshold, feaId, toChangeFeas, sumFilterFlag, mlpFilterFlag, normFilterFlag, voteFilterFlag

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

def loadDataArff(dataPath):
    datalist = []
    FeaNum = 0
    trueLabellist = []
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
                    trueLabellist.append(1)
                else:
                    trueLabellist.append(0)

                ## data's feature vector
                arr = list([float(val) for val in dataArr[:-1]])
                datalist.append(arr)
            break
        else:
            lineIdx += 1

    FeaNum = len(datalist[0])
    print "### Loading ends. " + str(time.asctime()) + " " + str(len(datalist)) + " items and " + str(FeaNum) + " features in each item are from " + dataPath
    return datalist, FeaNum, trueLabellist

def loadDataLibsvm(dataPath):
    datalist = []
    datalistTmp = []
    FeaNum = 0
    trueLabellist = []
    dataFile = file(dataPath)
    contentArr = dataFile.readlines()
    for dataStr in contentArr:
        dataStr = dataStr[:-1]
        dataArr = dataStr.split(" ")

        ## manually assigned label
        if dataArr[0] == "1":
            trueLabellist.append(1)
        else:
            trueLabellist.append(0)

        ## data's feature vector
        arr = list([float(val[val.find(":")+1:]) for val in dataArr[1:]])
        datalist.append(arr)

#    datalist = normFeatures(datalist)
#    datalist = strengthFeatures(datalist)
#    datalist = deleteFeatures(datalist)
    assignWeight(datalist)
#    datalist = mergeFeatures(datalist)
    FeaNum = len(datalist[0])
    print "### Loading ends. " + str(time.asctime()) + " " + str(len(datalist)) + " items and " + str(FeaNum) + " features in each item are from " + dataPath
    return datalist, FeaNum, trueLabellist

def assignWeight(datalistTmp):
    datalist = []
    for arr in datalistTmp:
        for i in range(len(manualPositiveSet)):
            fid = manualPositiveSet[i]
            arr[fid-1] = 1-arr[fid-1]
        datalist.append(arr)
    return datalist

def mergeFeatures(datalistTmp):
    print "### Merge features " + str(mergeFeas) + " when loading data."
    datalist = []
    for arr in datalistTmp:
        for merStr in mergeFeas:
            merIds = merStr.split("_")
            merIds = [int(val) for val in merIds]
            keptId = merIds[0]-1
            for merid in merIds[1:]:
                merid = merid-1
                arr[keptId] *= arr[merid]
                arr[merid] = 0.0
        datalist.append(arr) 
    return datalist

def normFeatures(datalistTmp):
    datalist = []
#    toNormFeas = toChangeFeas
    toNormFeas = [i for i in range(1,len(datalistTmp[0])+1)]
    maxVal = [0.0 for val in toNormFeas]
    minVal = [10000.0 for val in toNormFeas]
    for arr in datalistTmp:
        ## maxVal minVal for toNormFeas
        for i in range(len(toNormFeas)):
            fid = toNormFeas[i]
            if arr[fid-1] > maxVal[i]:
                maxVal[i] = arr[fid-1]
            if arr[fid-1] < minVal[i]:
                minVal[i] = arr[fid-1]
    print maxVal
    print minVal
    for arr in datalistTmp:
        for i in range(len(toNormFeas)):
            if maxVal[i] == minVal[i]:
                continue
            fid = toNormFeas[i]
            arr[fid-1] = (arr[fid-1]-minVal[i])/(maxVal[i]-minVal[i]) # normalize
        datalist.append(arr)
    return datalist

def strengthFeatures(datalistTmp):
    datalist = []
    for arrTmp in datalistTmp:
        arr = [val*2 for val in arrTmp]
        for i in range(len(toChangeFeas)):
            fid = toChangeFeas[i]
            arr[fid-1] = arr[fid-1]/4.0
        datalist.append(arr)
    return datalist

def deleteFeatures(datalistTmp):
    datalist = []
    for arr in datalistTmp:
        for i in range(len(toChangeFeas)):
            fid = toChangeFeas[i]
            arr[fid-1] = 0.0
        datalist.append(arr)
    return datalist

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
    print "#Extra resource: manual positive set: " + str(mPosSet)
    return centroids

def avgData(dataInside, FeaNum):
    centroid = [0.0 for i in range(FeaNum)]
    for data in dataInside:
        for i in range(FeaNum):
            centroid[i] += data[i]
    for i in range(FeaNum):
        centroid[i] = centroid[i] / len(dataInside)
    return centroid

def getPositiveSet(centroidHash, eventLabel):
    ## get extra resource
    sPosSet = []
    for i in range(1, 14):
        if centroidHash[eventLabel][i] > centroidHash[1-eventLabel][i]:
            sPosSet.append(i)
    return sPosSet

def unsupFilter(threshold, intervalNum, feaId):
    if normFilterFlag:
        dataHash = normFilter()
        print "### normFilter(<=" + str(threshold) + ")",
    elif sumFilterFlag:
        dataHash = sumFilter()
        print "### sumFilter(<=" + str(threshold) + ")",
    elif mlpFilterFlag:
        dataHash = mlpFilter()
        print "### mlpFilter(<=" + str(threshold) + ")",
    elif voteFilterFlag:
        dataHash = voteFilter(intervalNum)
        print "### voteFilter(>=" + str(FeaNum - threshold) + ")",
    elif feaId != 0:
        dataHash = featureFilter(feaId)
        print "### featureFilter",
    sortedEList = sorted(dataHash.items(), key = lambda a:a[1])
    [stNum, sNum, mtNum, pr, r, f1] = evaluateFilter(sortedEList, threshold)
    print  " P: " + str(pr) + " R: " + str(r) + " f1: " + str(f1)
    print "###stNum: " + str(stNum) + " sNum: " + str(sNum) + " mtNum: " + str(mtNum)
#    print str(pr) + "\t" + str(r) + "\t" + str(f1)
#    print str(stNum) + "\t" + str(sNum) + "\t" + str(mtNum)
    maxVal = max(dataHash.values())
    minVal = min(dataHash.values())
    [prDis, rDis, f1Dis] = output(sortedEList, maxVal, minVal, intervalNum, True)
    return stNum, sNum, mtNum, pr, r, f1

def normFilter():
    dataHash = {}
    for i in range(len(datalist)):
        data = datalist[i]
        score = math.sqrt(sum([val*val for val in data]))
        dataHash[i] = score
    return dataHash

def sumFilter():
    dataHash = {}
    for i in range(len(datalist)):
        data = datalist[i]
        score = sum(data)
        dataHash[i] = score
    return dataHash

def mlpFilter():
    dataHash = {}
    for i in range(len(datalist)):
        data = datalist[i]
        score = 1.0
        for val in data:
            if val == 0:
                val = 0.00001
            score *= val
        dataHash[i] = score
    return dataHash

def voteFilter(intervalNum):
    # use each feature as filter, tune parameters for each filter, and get their predict results with best parameters.
    parameterList = []
    resultList= []
#    manualBestId = [9, 13, 13, 1, 1, 1, 6, 6, 3, 14, 1, 15, 16, 5, 8, 4] # 16features
    manualBestId = [4, 13, 13, 1, 1, 1, 6, 6, 3, 14, 1, 15, 16, 5, 8, 4, 4] # 17 features_mu_sim
    for i in range(FeaNum):
        feaId = i+1
        dataHash = featureFilter(feaId)
        sortedEList = sorted(dataHash.items(), key = lambda a:a[1])
        maxVal = max(dataHash.values())
        minVal = min(dataHash.values())
        print "Feature " + str(feaId)
        [prDis, rDis, f1Dis] = output(sortedEList, maxVal, minVal, intervalNum, True)
        if False:
            outputToExcel(prDis, intervalNum)
            outputToExcel(rDis, intervalNum)
            outputToExcel(f1Dis, intervalNum)
        bestId = 0
        # select bestid
        bestId = manualBestId[i]
        step = (maxVal-minVal)/intervalNum
        bestThreshold = minVal + (bestId+1)*step
        if bestThreshold > maxVal:
            bestThreshold = maxVal
        parameterList.append(bestThreshold)
        para = bestThreshold
        tmpResultList = list([int(para-item[1]+1) for item in sortedEList])
#        print "### max: " + str(maxVal) + " min: " + str(minVal) + " step: " + str(step) + " bestid: " + str(bestId)
#        print "bestThre: " + str(bestThreshold)
#        print tmpResultList
        if len(resultList) == 0:
            resultList = [val for val in tmpResultList]
        else:
            resultList = [resultList[i]+tmpResultList[i] for i in range(len(tmpResultList))]
    dataHash = dict([(i, FeaNum-resultList[i]) for i in range(len(resultList))]) 
    return dataHash

def featureFilter(feaId):
    dataHash = {}
    for i in range(len(datalist)):
        data = datalist[i]
        score = data[feaId-1]
        dataHash[i] = score
    return dataHash

def output(sortedList, maxVal, minVal, intervalNum, outputFlag):
    step = (maxVal-minVal)/intervalNum
    if step == 0:
        prDis = dict([(i, 0.0) for i in range(intervalNum)])
        return prDis, prDis, prDis
    scoreIdxDis = {}
    trueScoreIdxDis = {}
    falseScoreIdxDis = {}
    for item in sortedList:
        i = item[0]
        score = item[1]
        scoreIdx = int((score-minVal)/step)
        if score == maxVal:
            scoreIdx = intervalNum-1
        if scoreIdx in scoreIdxDis:
            scoreIdxDis[scoreIdx] += 1
        else:
            scoreIdxDis[scoreIdx] = 1
        if trueLabellist[i] == 1:
            if scoreIdx in trueScoreIdxDis:
                trueScoreIdxDis[scoreIdx] += 1
            else:
                trueScoreIdxDis[scoreIdx] = 1
        else:
            if scoreIdx in falseScoreIdxDis:
                falseScoreIdxDis[scoreIdx] += 1
            else:
                falseScoreIdxDis[scoreIdx] = 1
 #       if outputFlag:
        if False:
            print "Event " + str(i) + " m" + str(trueLabellist[i]) + " score: " + str(score)
            if FeaNum > 1000:
                print "PartFeature: " + str(datalist[i][0:20])
            else:
                print "Features" + str(datalist[i])

    scoreDis = dict([(str(idx).zfill(2)+"_"+str(round(minVal+(idx+1)*step, 5)), scoreIdxDis[idx]) for idx in scoreIdxDis])
    trueScoreDis = dict([(str(idx).zfill(2)+"_"+str(round(minVal+(idx+1)*step, 5)), trueScoreIdxDis[idx]) for idx in trueScoreIdxDis])
    falseScoreDis = dict([(str(idx).zfill(2)+"_"+str(round(minVal+(idx+1)*step, 5)), falseScoreIdxDis[idx]) for idx in falseScoreIdxDis])
    num = 0
    tnum = 0
    prDis = {}
    rDis = {}
    f1Dis = {}
    for i in range(intervalNum):
        if i in scoreIdxDis:
            num += scoreIdxDis[i]
        if i in trueScoreIdxDis:
            tnum += trueScoreIdxDis[i]
        [pr, r, f1] = getMetric(tnum, num, 804)
        prDis[i] = pr
        rDis[i] = r
        f1Dis[i] = f1
    if outputFlag:
        print "### score distribution: max: " + str(maxVal) + " min: " + str(minVal) + " step: " + str(step)
        print "\t".join(sorted(scoreDis.keys()))
    #    print sorted(scoreDis.items(), key = lambda a:a[1], reverse = True)
    #    print sorted(trueScoreDis.items(), key = lambda a:a[1], reverse = True)
    #    print sorted(falseScoreDis.items(), key = lambda a:a[1], reverse = True)
        if "-f" in sys.argv:
            print "### feature " + str(feaId)
        outputToExcel(trueScoreIdxDis, intervalNum)
        outputToExcel(falseScoreIdxDis, intervalNum)
        outputToExcel(scoreIdxDis, intervalNum)
        outputToExcel(prDis, intervalNum)
        outputToExcel(rDis, intervalNum)
        outputToExcel(f1Dis, intervalNum)
    return prDis, rDis, f1Dis

def outputToExcel(hashmap, intervalNum):
    for idx in range(0, intervalNum):
        score = 0
        if idx in hashmap:
            score = hashmap[idx]
        if idx == 0:
            print str(score),
        else:
            print "\t" + str(score),
    print "" 

def evaluateFilter(sortedList, threshold):
    stNum = 0
    sNum = 0
    mtNum = sum(trueLabellist)
    for item in sortedList:
        i = item[0]
        score = item[1]
        if score <= threshold:
            sNum += 1
            if trueLabellist[i] == 1:
                stNum += 1
    [pr, r, f1] = getMetric(stNum, sNum, mtNum)
    return stNum, sNum, mtNum, pr, r, f1

def getMetric(stNum, sNum, mtNum):
    pr = 0.0
    r = 0.0
    f1 = 0.0
    if stNum > 0:
        pr = stNum*1.0/sNum
        r = stNum*1.0/mtNum
        f1 = 2*pr*r/(pr+r)
    return round(pr, 4), round(r, 4), round(f1, 4)

#####################################################################
## main function
print "### " + str(time.asctime()) + " k-means filter program starts."
global datalist, FeaNum, trueLabellist, manualCentroid
dirPath = r"../Data_hfmon/segged_ltwe/classify/"
print sys.argv
global toChangeFeas, sumFilterFlag, mlpFilterFlag, normFilterFlag, voteFilterFlag
[suffix, scoreThreshold, feaId, toChangeFeas, sumFilterFlag, mlpFilterFlag, normFilterFlag, voteFilterFlag] = getparameter()
global manualPositiveSet
manualPositiveSet= [1, 2, 3, 4, 8, 10, 12, 13, 17] #mpos2Temp
global mergeFeas
#mergeFeas = ["2_3", "5_6", "7_8_9"]
mid = 3
#mergeFeas = mergeFeas[mid:mid+1] # select one
#del mergeFeas[mid] # select two
#del mergeFeas[:] # don't merge features
#mergeFeas = ["14_15_16"]


dataPath = dirPath + r"EventDataset_All" + suffix + ".libsvm"
[datalist, FeaNum, trueLabellist] = loadDataLibsvm(dataPath)
manualCentroid = getManualCentroid()

intervalNum = 30
unsupFilter(scoreThreshold, intervalNum, feaId)
print "### " + str(time.asctime()) + " program ends."
print "********************************************************************"
