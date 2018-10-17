import argparse

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