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
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.hostName, self.portNumber))
        sock.sendall(bytes(json.dumps((string, data)), encoding='utf-8'))
        v = sock.recv(self.BUFFER_SIZE)
        self.status = json.loads(v)
        sock.close()
        del sock

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
