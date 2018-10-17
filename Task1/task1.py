#!/usr/bin/env python2
# encoding=utf8
import sys
import psutil
import os
import pprint
from Core.Logger import logger
from Core.common_functions import call_subprocess as sh
from helper_functions import parse_script_commandline_arguments as parse_args
from Core.SSH import Host

FILES_TO_CLEATE = 10

def get_patitions_with_free_space(partitions_list, expected_size_bytes):
    result = []
    for partition in partitions_list:
        if int(partition.split()[0]) >= expected_size_bytes:
            result.append(partition)
    return result

def check_disk(args):
    logger.info(pprint.PrettyPrinter(indent=2, width=400).pformat(args))
    logger.info(message="> Task 1 called.")
    remote_SSH_host = Host(args)
    logger.echo(message="> Connecting to {name}.".format(name=str(remote_SSH_host)),
                color=logger.OKGREEN)

    if remote_SSH_host.ssh_connect():
        cmd = "lsblk -l -b | awk 'NR>1 && /.*part.*/ {print $4, $6, $7}'"
        cmd_result = remote_SSH_host.exec_remote_command(cmd)
        pprint.PrettyPrinter(indent=2).pprint(cmd_result)
        remote_SSH_host.ssh_close()

    partitions_list = [ line.encode('utf-8') for line in cmd_result['stdout'] ]
    patitions_available = get_patitions_with_free_space(partitions_list, 1073741824) # 1073741824 =1GB
    pprint.PrettyPrinter(indent=2, width=400).pprint(patitions_available)

    remote_SSH_host = Host(args)
    if patitions_available:
        if remote_SSH_host.ssh_connect():
            mount_point = patitions_available[0].split()[-1]
            mount_point = mount_point[:-1] if mount_point[-1] == '/' else mount_point
            for i in range(FILES_TO_CLEATE):
                cmd = "sudo mkdir -p {mount_point}/somedir ".format(mount_point=mount_point, i=i)
                cmd += "&& sudo chown -R {user} {mount_point}/somedir ".format(user=args.user, mount_point=mount_point, i=i)
                cmd += "&& touch {mount_point}/somedir/{i} ".format(mount_point=mount_point, i=i)
                cmd += "&& dd if=/dev/zero bs=5242880 count=1 >> {mount_point}/somedir/{i} ".format(mount_point=mount_point, i=i)
                cmd_result = remote_SSH_host.exec_remote_command(cmd)
    remote_SSH_host.ssh_close()


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    logger.log('\n\n*****************')
    logger.log("{args}".format(args=" ".join(sys.argv)))

    func_map = {
        'checkDisk': check_disk,
    }

    args = parse_args(func_map)
    func = func_map[args.action]

    func(args)
    logger.info(message="> Infrastructure Provision finished.")