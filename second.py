import sys
import subprocess
import commands
import threading

user = str(sys.argv[1])
host_1 = str(sys.argv[2])
host_2 = str(sys.argv[3])
user_command = str(sys.argv[4])

if (user == "" or host_1 == "" or host_2 == "" or user_command == ""):
    print "Wrong input data"
    exit(-1)
hosts = [host_1, host_2]
for host in hosts:
    cmd = "ssh "+user+"@"+host+" '"+user_command+"'"
    cmdOutput = commands.getoutput(cmd)
    print cmdOutput
