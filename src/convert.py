_conversion = {'inches': 1, 'mm': 25.4, 'cm': 2.54}

def convert(val, fromUnits, toUnits):
    if fromUnits == toUnits:
        return val
    unitConv = _conversion[toUnits] / _conversion[fromUnits]
    return val*unitConv
