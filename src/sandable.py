class Sandable():
    """ Base class for sandtable drawable classes. """
    editor = []

    def generate(self, params):
        return []


def sandableFactory(sandable, width, length, ballSize, units):
    """ Dynamically load and instantiate a drawable object. """
    from importlib import import_module

    sm = import_module('draw.%s' % sandable)
    return sm.Sander(width, length, ballSize, units)


class SandException(BaseException):
    pass


def inchesToUnits(value, units):
    return value * {'mm': 25.4, 'cm': 2.54}.get(units, 1)
