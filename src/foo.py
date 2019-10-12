import serial
import socket
import socketserver
import random
import time
from threading import Thread, Event 

class ReadThread(Thread):
    okCount = 0 

    def __init__(self,ser):
        self.ser = ser
        super(ReadThread, self).__init__()

    def run(self):
        self.running = True
        while self.running:
            line = self.ser.readline().strip()
            if len(line):
                print("<",line)
                if line.startswith('ok'):
                    self.okCount += 1

    def decrement(self):
        self.okCount -= 1

    def stop(self):
        self.running = False


ser = serial.Serial('/dev/ttyACM0',115200,timeout=.5, rtscts=True)
# Start the read thread
reader = ReadThread(ser)
reader.start()

program = []
program.append(b"M211 S0; Disable soft limits")
program.append(b"M17; Enable motors")
program.append(b"G0 F10000; Set feed rate")

for i in range(30):
    x = random.randint(0,1000)
    y = random.randint(0,1000)
    s = b"G0 X%d Y%d" % (x,y)
    program.append(s)

#program.append(b"M400")
program.append(b"M114")
program.append(b"M18")

for s in program:
    while reader.okCount < 0:
        time.sleep(.1)
    reader.decrement()
    print(">",s)
    ser.write(s + b"\n")

time.sleep(30.)
reader.stop()


