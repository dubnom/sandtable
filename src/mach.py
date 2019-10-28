import socket
import json
from Sand import MACH_HOST, MACH_PORT
from Chains import Chains


class mach:
    def __init__(self, hostName=MACH_HOST, portNumber=MACH_PORT):
        self.hostName = hostName
        self.portNumber = portNumber
        self.BUFFER_SIZE = 512
        self.status = None

    def __enter__(self):
        return self

    def __exit__(self, e, t, tb):
        return False

    def command(self, string, data={}):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.hostName, self.portNumber))
            cmd = bytes(json.dumps((string, data))+'\n', encoding='utf-8')
            sock.sendall(cmd)
            v = str(sock.recv(self.BUFFER_SIZE), 'utf-8')
            self.status = json.loads(v)

    def close(self):
        pass

    def run(self, chains, box, feed, tableUnits, machUnits,  wait=False):
        chains = Chains.bound(chains, box)
        chains = Chains.convertUnits(chains, tableUnits, machUnits)
        chains = Chains.round(chains, 2)
        self.command('run', {'chains': chains, 'wait': wait, 'feed': feed, 'units': machUnits})

    def stop(self):
        self.command('halt')

    def restart(self):
        self.command('restart')

    def home(self):
        self.command('home')

    def getStatus(self):
        self.command('status')
        return self.status
