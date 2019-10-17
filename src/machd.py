#!/usr/bin/python3
import logging
from Sand import *
from importlib import import_module


logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)
machine = import_module('machines.%s' % MACHINE)

# Check settings update file
fullInitialization = True
with open(MACH_FILE,'r') as f:
    newVersion = f.read()

try:
    with open(VER_FILE,'r') as f:
        oldVersion = f.read()
    if oldVersion == newVersion:
        fullInitialization = False
except Exception as e:
    logging.error(e)

if fullInitialization:
    with open(VER_FILE,'w') as f:
        f.write(newVersion)

machine.runMachine(fullInitialization)
exit(1)
