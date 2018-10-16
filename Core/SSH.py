import os
import pwd
import paramiko
from StringIO import StringIO
from Core.Logger import logger


class Host:
    def __init__(self, args):
        self.args = args
        self.port = args.port
        self.address = args.address
        self.ssh_client = paramiko.SSHClient()
        self.sftp = None
        self.isConnected = False

    def __str__(self):
        return self.address + ":" + str(self.port)

    def get_key(self, key_file_name):
        f = open(os.path.expanduser(key_file_name), 'r')
        s = f.read()
        key_file = StringIO(s)
        return paramiko.RSAKey.from_private_key(key_file)

    def ssh_close(self):
        if (self.isConnected):
            self.sftp.close()
            self.ssh_client.close()
            logger.info("SSH connection has been closed.")

    def ssh_connect(self):
        if not self.isConnected:
            self.ssh_client.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())
            key = self.get_key(self.args.ssh_private_key)
            username = self.args.user if self.args.user else pwd.getpwuid(os.getuid())[0]

            try:
                self.ssh_client.connect(self.address,
                                        port=self.port,
                                        username=username,
                                        pkey=key,
                                        timeout=5)
                self.sftp = self.ssh_client.open_sftp()
                self.isConnected = True
                logger.info("SSH connection to {host} has been established.".format(host=self.address))
                return True
            except (paramiko.BadHostKeyException,
                    paramiko.AuthenticationException,
                    paramiko.ssh_exception.NoValidConnectionsError) as e:
                logger.error(str(e))
                return False
        else:
            return True

    def exec_remote_command(self, command):
        if self.isConnected:
            self.ssh_client.get_transport().open_session()
            try:
                stdin_raw, stdout_raw, stderr_raw = \
                    self.ssh_client.exec_command(command)
                stdout = stdout_raw.read().decode()
                stderr = stderr_raw.read().decode()
                cmd_result = {"stdout": [], "stderr": []}
                if stdout:
                    logger.info(stdout)
                    cmd_result['stdout'] = stdout.splitlines()
                if stderr:
                    logger.error(stderr)
                    cmd_result['stderr'] = stderr.splitlines()
                return cmd_result
            except (paramiko.SSHException) as e:
                logger.error("SSH error({0}): {1}".format(e.errno, e.strerror))
        else:
            logger.error("The host ssh channel is not opened.")
            return False

    def remote_file_exists(self, file):
        if self.isConnected:
            try:
                self.sftp.stat(file)
                return True
            except IOError as e:
                logger.error(e.strerror)
                return False
        else:
            logger.error("The host is not connected via SSH.")
            return False