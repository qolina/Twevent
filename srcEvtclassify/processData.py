import os
import random
import math
import time
import sys

# get parameters
def getparameter():
    inSuffix = ""
    outSuffix = ""
    toChangeFeas = []
    if len(sys.argv) == 1:
        print "Usage: processData.py [-c toChangeFeas] -in inputfile -o outputSuffix"
        sys.exit()
    if "-in" in sys.argv:
        inSuffix += sys.argv[sys.argv.index("-in")+1]
    if "-o" in sys.argv:
        outSuffix += sys.argv[sys.argv.index("-o")+1]
    if "-c" in sys.argv:
        toDelFeasStr = sys.argv[sys.argv.index("-c")+1]
        arr = toDelFeasStr.split("_")
        toChangeFeas = list([int(val) for val in arr])
    return inSuffix, outSuffix, toChangeFeas

def loadDataLibsvm(dataPath):
    datalist = []
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

#    toNormFeas = toChangeFeas
    toNormFeas = [i for i in range(1,len(datalist[0])+1)]
    datalist = normFeatures(datalist, toNormFeas)
#    datalist = strengthFeatures(datalist, toChangeFeas)
    datalist = deleteFeatures(datalist, toChangeFeas)
#    assignWeight(datalist)
    datalist = mergeFeatures(datalist)
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
               # arr[merid] = 0.0
                del arr[merid]
        datalist.append(arr) 
    return datalist

def normFeatures(datalistTmp, toNormFeas):
    datalist = []
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

def strengthFeatures(datalistTmp, toIncreaseFeas):
    datalist = []
    for arrTmp in datalistTmp:
        arr = [val*2 for val in arrTmp]
        for i in range(len(toIncreaseFeas)):
            fid = toIncreaseFeas[i]
            arr[fid-1] = arr[fid-1]/4.0
        datalist.append(arr)
    return datalist

def deleteFeatures(datalistTmp, toDelFeas):
    datalist = []
    for arr in datalistTmp:
        arrTmp = []
        for i in range(len(arr)):
            if (i+1) in toDelFeas:
                continue
            arrTmp.append(arr[i])

        datalist.append(arrTmp)
    return datalist

def outputFeature(outputFilePath):
    outFile = file(outputFilePath, "w")
    for instId in range(len(datalist)):
        data = datalist[instId]
        newFeatures = []
        for val in data:
            newFeas = toBins(val)
            newFeas = [val]
            newFeatures.extend(newFeas)
#        print "id: " + str(instId) + " " + str(sum(newFeatures))
#        if sum(newFeatures) != 17:
#            print "Error! to binary features wrong."
        newFeatures = [str(i+1)+":"+str(newFeatures[i]) for i in range(len(newFeatures))]
        outFile.write(str(trueLabellist[instId]) + " " + " ".join(newFeatures) + "\n")
    outFile.close()
            
def toBins(val):
    binFea = [0 for i in range(10)]
    binfId = int(val*10)
    if binfId == 10:
        binfId -= 1
    binFea[binfId] = 1
    return binFea
#####################################################################
## main function
print "### " + str(time.asctime()) + " binary data program starts."
global datalist, FeaNum, trueLabellist
dirPath = r"../Data_hfmon/segged_ltwe/classify/"
print sys.argv
global toChangeFeas, sumFilterFlag, mlpFilterFlag, normFilterFlag, voteFilterFlag
[inSuffix, outSuffix, toChangeFeas] = getparameter()
global manualPositiveSet
manualPositiveSet= [1, 2, 3, 4, 8, 10, 12, 13, 17] #mpos2Temp
global mergeFeas
mergeFeas = ["13_14"]
mergeFeas = []

intervalNum = 30
#dataPath = dirPath + r"EventDataset_All" + inSuffix + ".libsvm"
dirPath = r"../libsvm/musim3/"
dataPath = dirPath + inSuffix + ".libsvm"
[datalist, FeaNum, trueLabellist] = loadDataLibsvm(dataPath)

outputFilePath = dirPath + inSuffix + "_" + outSuffix + ".libsvm"
outputFeature(outputFilePath)
print "### new features writen to " + outputFilePath
print "### " + str(time.asctime()) + " program ends."
print "********************************************************************"
