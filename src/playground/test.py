from math import *

def humanStep(number,ticks):
    if number == 0.:
        return 1.
    if ticks <= 1:
        return number
    tickSize = number / (ticks-1)
    scale = pow(10,ceil( log10(tickSize)-1 ))
    n = tickSize / scale
    for step in [10.,5.,2.5,2.,1.]:
        if n > step:
            return step * scale
    return None

print(humanStep(3.1415,2))
print(humanStep(542.5,10))   
    







from Sand import *
from Chains import *
from machines.version3 import *

chains = [
    [[0,0], [30,0], [30,20], [0,20], [0,0]],
]

print(Chains.estimateMachiningTime( chains, [[0,0],[30,20]], TABLE_FEED, 1.5 )) #TABLE_ACCEL ) 

chains = [
#    [[10,10], [15,10], [15,15], [10,15], [10,10]],
    [[0,0], [10,5], [20,15], [30,20]],
]

print(Chains.splines(chains,5))
