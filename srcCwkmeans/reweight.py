import sys

str2ID = dict()
ID2weight = dict()

pos = -1

f = file(sys.argv[1])
while True:
    line = f.readline()

    if len(line) == 0:
        break

    line = line.split('\n')[0]

#MAPPING string->ID
    if line == "==featuremap==":
        pos = 0
        continue


#WEIGHTS ID->weight
    if line == "==weights==":
        pos = 1
        continue

#DONE
    if line == "==covariance==":
        break


    if pos == 0:
        str2ID[line.split(' ')[0]] = line.split(' ')[1]
        
    if pos >= 1:
        ID2weight[pos-1] = line
        pos = pos + 1
f.close()

f3 = file(sys.argv[3], 'w')

f2 = file(sys.argv[2])
while True:
    line = f2.readline()
    if len(line) == 0:
        break

    vec = line.split(' ') 
    newLine = vec[0];
    for i in xrange(1, len(vec)):
        vec[i].split(':')
        newLine = newLine + " " + vec[i].split(':')[0] + ":" + str(float(vec[i].split(':')[1]) * float(ID2weight[int(str2ID[vec[i].split(':')[0]])]))
#        newLine = newLine + " " + vec[i].split(':')[0] + ":" + str(float(vec[i].split(':')[1]) * float(ID2weight[i-1]))

    f3.write(newLine + '\n')
f2.close()

f3.close()
