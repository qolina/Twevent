import sys

prefixDict = {}

lineNum = 0

print sys.argv

f = file(sys.argv[2])
while True:
    line = f.readline()
    if len(line) == 0:
        break

    lineNum = lineNum + 1
    if (lineNum) % 10000 == 0:
        print "Processing line " + str(lineNum) + "..." + str(len(prefixDict))

    cols = line.split('\t')
    if len(cols) != 2:
        print "Invalid format: " + line

    prefix= cols[0]
    tf = float(cols[1][:-1])
    if tf < float(sys.argv[1]):
        break
    prefixDict[prefix]  = tf;

f.close()

prefixFile = file(sys.argv[3], 'w')
idx = 0
preWord = ""
for key in sorted(prefixDict.items(), key = lambda a:a[0]):
    idx += 1
    if idx == 0:
        preWord = key[0]
        continue
    prefixFile.write("%s\t%f\n" % (key[0], key[1]))
prefixFile.close()

