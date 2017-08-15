import sys

weight = sys.argv[4] == "weight"

prefixDict = {}
suffixDict = {}

lineNum = 0

f = file(sys.argv[1])
while True:
    line = f.readline()
    if len(line) == 0:
        break

    lineNum = lineNum + 1
    if (lineNum) % 10000 == 0:
        print "Processing line " + str(lineNum) + "..."

    cols = line.split('\t')
    if len(cols) != 3:
        print "Invalid format: " + line

    tag = cols[0].lower()
    for i in xrange(len(cols[0]) - 1):

        prefix = tag[1:i+2]
        suffix = tag[i+1:len(tag)]

        if prefixDict.get(prefix) == None:
            prefixDict[prefix]  = 0;

        if weight:
            prefixDict[prefix] += float(cols[1])
        else:
            prefixDict[prefix] += 1.0

        if suffixDict.get(suffix) == None:
            suffixDict[suffix]  = 0;

        if weight:
            suffixDict[suffix] += float(cols[1])
        else:
            suffixDict[suffix] += 1.0
f.close()

prefixFile = file(sys.argv[2], 'w')
for key in sorted(prefixDict.items(), key = lambda a:a[1], reverse = True):
    prefixFile.write("%s\t%f\n" % (key[0], key[1]))
prefixFile.close()

suffixFile = file(sys.argv[3], 'w')
for key in sorted(suffixDict.items(), key = lambda a:a[1], reverse = True):
    suffixFile.write("%s\t%f\n" % (key[0], key[1]))
suffixFile.close()
