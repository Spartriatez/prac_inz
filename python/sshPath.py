import paramiko
import warnings
import os
from formencode import variabledecode

warnings.filterwarnings(action='ignore', module='.*paramiko.*')


class Ssh:
    client = None

    def __init__(self, address, username, password):
        print("Connecting to server.")
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        # self.client.connect(address, username=username, password=password, look_for_keys=False)
        self.client.connect(address, username=username, pkey=mykey)

    def sendCommand(self, command):
        data = None
        if (self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Print data when available
                if stdout.channel.recv_ready():
                    alldata = stdout.channel.recv(1024)
                    prevdata = b"1"
                    while prevdata:
                        prevdata = stdout.channel.recv(1024)
                        alldata += prevdata
                    data = str(alldata, "utf8")
        else:
            print("Connection not opened.")
            data = None
        if data is None:
            postvars = []
        else:
            postvars = data.split("\n")
            postvars = [x[:-1] for x in postvars]
        return postvars

    def send_path(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        data = stdout.read()
        data=data.decode("utf-8")
        return data[:-1]

    def git_Command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        output=""
        data = stdout.readlines()
        for line in data:
            output+=line
        return output

    def git_Command2(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        output=""
        err=""
        er=stderr.readlines()
        data = stdout.readlines()
        for line in data:
            output+=line
        for errline in er:
            err += errline
        return output,err

def check_exist_ssh(ssh_path):
    data=ssh_path.split('://')
    if(data[0]=='ssh'):
        return 1
    else:
        return 0

def split_data(ssh_path):
    data=ssh_path.split('://')
    us_host=data[1].split('@')
    user=us_host[0]

    tmp=us_host[1].split('/')
    hostname=tmp[0]
    del tmp[0]
    pathname='/'+'/'.join(tmp)
    return user,hostname,pathname