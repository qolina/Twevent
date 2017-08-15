import sys

lineNum = 0

preStr=""
preSco=0

iFile = file(sys.argv[1])
oFile = file(sys.argv[2], 'w')
while True:
    line = iFile.readline()
    if len(line) == 0:
        break

    lineNum = lineNum + 1
    if (lineNum) % 10000 == 0:
        print "Processing line " + str(lineNum) + "..."

    cols = line.split('\t')
    if len(cols) != 2 or len(cols[0]) == 0:
        print "Invalid format: " + line
        continue

    if len(preStr) == 0 or cols[0].startswith(preStr):
        preStr = cols[0] 
        preSco = cols[1] 
        continue

    oFile.write(preStr + '\t' + preSco)
    preStr = cols[0] 
    preSco = cols[1] 
 

if len(preStr) != 0:
    oFile.write(preStr + '\t' + preSco)

iFile.close()
oFile.close()
