#!/usr/bin/python
import logging
from Sand import *

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)
exec("from %s import *" % MACHINE)
runMachine()
exit(1)
