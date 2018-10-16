import os
import subprocess
import argparse
from Core.Logger import logger

def call_subprocess(cmd, args, env_vars={}):
    child = subprocess.Popen(cmd.split(), env=env_vars, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd_result = {"stdout":[],"stderr":[]}
    while child.poll() is None:
        for line in iter(child.stdout.readline, b''):
            formated_string=line.decode().replace(line[:-1] if line[-1] == os.linesep else '\n', '')
            cmd_result["stdout"].append(formated_string)
            if args.debug:
                logger.info(message=formated_string)
        for line in iter(child.stderr.readline, b''):
            formated_string = line.decode().replace(line[:-1] if line[-1] == os.linesep else '\n', '')
            cmd_result["stderr"].append(formated_string)
            if args.debug:
                logger.error(message=formated_string)
    child.communicate()
    return cmd_result


def parse_script_commandline_arguments(func_map):

    p = argparse.ArgumentParser()
    p.add_argument('action', choices=func_map.keys())
    p.add_argument('address', default="127.0.0.1", help="remote host address")
    p.add_argument('-p', '--port', default=22, type=int, help="remote host port", action="store")
    p.add_argument('-u', '--user', default="vagrant", help="remote user", action="store")
    p.add_argument('--debug', default=False, help="debug output", action="store_true")
    p.add_argument('-i', '--ssh-private-key', default="~/.ssh/id_rsa", help="SSH private key file", action="store_true")
    args = p.parse_args()
    return args