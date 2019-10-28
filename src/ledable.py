class Ledable():
    """ Base class for led lighting classes. """
    editor = []

    def generator(self, leds, params):
        pass


def ledPatternFactory(pattern, columns, rows):
    """ Dynamically load and instantiate led patterns. """
    from importlib import import_module

    lm = import_module('lights.%s' % pattern)
    return lm.Lighter(columns, rows)
