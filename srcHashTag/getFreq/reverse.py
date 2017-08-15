import sys

lineNum = 0

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

    oFile.write(cols[0][::-1] + '\t' + cols[1])

iFile.close()
oFile.close()
