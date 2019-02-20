#!/usr/bin/env python
import subprocess


serverList = ["artem@192.168.0.3:22", "artem@192.168.0.3:223"]
command = "ls"

for server in serverList:
    serverparams=server.split(":")
    o = subprocess.check_output(['ssh', '-p %s' %serverparams[1], '%s' %serverparams[0], '%s' %command], stderr=subprocess.STDOUT)
    print(o)
