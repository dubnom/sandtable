#!/usr/bin/python3
import logging
from Sand import *

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)
exec("from machines.%s import *" % MACHINE)
runMachine()
exit(1)
