#!/usr/bin/env python
import psutil
import platform
import subprocess
import os
from datetime import datetime
from time import time

print('Enter the size availble for files:')
X = input()
print('Enter the amount of files:')
Z = input()
print('Enter the file sizes block size(bs):')
bs = input()
bs='bs=%dK' % bs
print('Enter the block count(count):')
count = input()
count='count=%d' % count

partitions = psutil.disk_partitions()

for partition in partitions:
    if partition.fstype == "xfs" and \
            psutil.disk_usage(partition.mountpoint).free > int(X):
        Z1 = int(Z)
        start_t = time()
        for i in range(0, Z1):
            test_file = "test_file"+str(i)
            out_fd = open(test_file,'w')
            out_fd.write('start \n')
            of='of=/dev/shm/'+test_file
            cmd_list = ['dd','if=/dev/urandom', of, bs,count]
            a = subprocess.Popen(cmd_list,stderr=out_fd)
            # a.communicate()
        for i in range(0, Z1):
            os.wait()
        stop_t = time()
        print("Elapesed %.3f seconds" % (stop_t - start_t))
