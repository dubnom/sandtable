from Sand import LED_HOST, LED_PORT, LED_COLUMNS, LED_ROWS
import socket
import json
import pickle
from importlib import import_module


def ledPatternFactory(pattern):
    lm = import_module('lights.%s' % pattern)
    return lm.Lighter(LED_COLUMNS, LED_ROWS)


def setLedPattern(pattern, params):
    with ledApi() as api:
        return api.setPattern(pattern, params)


class ledApi:
    def __init__(self, hostName=LED_HOST, hostPort=LED_PORT):
        self.hostName = hostName
        self.hostPort = hostPort
        self.BUFFER_SIZE = 512
        self._status = None

    def __enter__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.hostName, self.hostPort))
        return self

    def __exit__(self, e, t, tb):
        self.sock.close()
        del self.sock
        return False

    def command(self, cmd, pattern=None, params=None):
        self.sock.sendall(pickle.dumps((cmd, pattern, params)))
        self._status = json.loads(self.sock.recv(512).decode('utf-8'))
        return self._status

    def setPattern(self, pattern, params):
        return self.command('pattern', pattern, params)

    def status(self):
        return self.command('status')

    def restart(self):
        return self.command('restart')
