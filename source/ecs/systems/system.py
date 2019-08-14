# system.py

"""Base system class"""

from messenger import Logger


class System(object):
    def __init__(self, engine, logger=None):
        # reference to the engine object
        self.engine = engine
        # if a logger is passed in it will overwrite the logger instance
        # if not then a new logger will be created
        self.logger = logger if logger else Logger()

    @classmethod
    def classname(cls):
        return cls.__name__.lower()

    def process(self):
        raise NotImplementedError("Implement base system process method")
