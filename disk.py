#!/usr/bin/env python
import pyudev
import psutil
import subprocess

# of course, we can use sys.argv but just for quick test this more useful
freeSpaceGB = 10
fileName = "testFile"
fileSizeMB = 10

context = pyudev.Context()
# I have some flash drivers, so can easily test it
# in case, if we want use it for some not removable devices,
# we should use device.attributes.asstring('removable') == "0"
removable = [device for device in context.list_devices(subsystem='block', DEVTYPE='disk') if device.attributes.asstring('removable') == "1"]
for device in removable:
    partitions = [device.device_node for device in context.list_devices(subsystem='block', DEVTYPE='partition', parent=device)]
    print("All removable partitions: {}".format(", ".join(partitions)))
    print("Mounted removable partitions:")
    for p in psutil.disk_partitions():
        if p.device in partitions:
            obj_Disk = psutil.disk_usage(p.mountpoint)
            if (obj_Disk.free / (1024.0 ** 3)) >=freeSpaceGB:
                # we have enough space, go to create file
                fullFilePath = p.mountpoint + "/" + fileName
                open(fullFilePath, 'w').close()
                o = subprocess.check_output(
                    ['dd', 'if=/dev/zero', 'of=%s' %fullFilePath, 'count=1048576', 'bs=%i' %fileSizeMB], stderr=subprocess.STDOUT)
                print (o)