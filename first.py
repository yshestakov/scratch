import sys
import subprocess
import string
import time
import commands

start_time = time.time()
X = int(sys.argv[1])
Y = int(sys.argv[2])
Z = int(sys.argv[3])
Data = str(sys.argv[4])

if (X * 1024 < Y * Z) or (X < 1) or (Y < 1) or (Z < 1):
    print "Wrong input data."
    exit()
commandString = "df -m | grep -E '^/dev/' | awk '{print $6 \" \" $4 }'"
commandOutput = commands.getoutput(commandString)
findDisks = string.split(commandOutput, "\n")

for disk in findDisks:
    disk = disk.split()
    if disk[1] > X:
        break

for i in range(Z):
    size = 'bs=' + str(Y)
    name = disk[0]+"file_"+str(i+1)
    print name
    code = subprocess.call(["dd", "if=/dev/zero", "of="+name, size, "count=1024"])
    file = open(name, "w")
    file.write(Data)

print (time.time() - start_time)
