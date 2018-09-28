import os
#import subprocess
import paramiko

hosts = []
connections = []

# Create a hosts lit
def add_host(host):
    if host:
        hosts.append(host.split(","))
    else:
        print("Add a hostname or IP-address of a host, separated with comma")


# Open SSH-connections to all hosts in the 'hosts'-list
def ssh_open():
    for host in hosts:
        if user and ssh_key:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(username=user, key_filename=ssh_key, hostname=host)
            connections.append(ssh)

# Run a command specified in 'cmd'-variable
def run_cmd():
    output = []

    if cmd:
        for host, ssh in zip(hosts, connections):
            stdin, stdout, stderr = ssh.exec_command(cmd)
            for line in stdout.read().splitlines():
                print('host: %s: %s' % (host, line))
    else:
        print("Please, specify the command 'cmd' to run")

#Close opened SSH-connections
def ssh_close():
    for ssh in connections:
        ssh.close()

user = "ec2-user"
ssh_key = os.path.abspath(".ssh/skul.pem")
cmd = "ls -l"

# Add hosts list, separeted with ','
add_host("192.168.7.12,127.0.0.1")
ssh_open()
run_cmd()
ssh_close()
