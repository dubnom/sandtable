import os
import pickle
from Sand import MOVIE_STATUS_FILE
from datetime import datetime


class MovieStatus:
    """MovieStatus is used to maintain the status of spawned processes making movies"""
    ST_DONE = 0
    ST_RUNNING = 1
    ST_ERROR = 2
    ST_UNKNOWN = 3

    def __init__(self):
        self.status = self.ST_UNKNOWN
        self.pid = 0
        self.text = ''
        self.time = datetime.today()

    def update(self, status, text):
        self.pid = os.getpid()
        self.time = datetime.today()
        self.status = status
        self.text = text
        self.save()
        print(repr(self))

    def save(self):
        fp = open(MOVIE_STATUS_FILE, 'wb')
        pickle.dump(self, fp)
        fp.close()
        del fp

    def load(self):
        try:
            with open(MOVIE_STATUS_FILE, 'rb') as fp:
                ret = pickle.load(fp)
            self.pid = ret.pid
            self.time = ret.time
            self.status = ret.status
            self.text = ret.text
        except Exception:
            self.__init__()

    def __repr__(self):
        return '%d %s %s: %s' % (self.pid, self.time.strftime('%I:%M:%S'), ('Done', 'Running', 'Error', 'Unknown')[self.status], self.text)
