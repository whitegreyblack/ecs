# system.py

"""Base system class"""

from source.logger import Logger


class System(object):
    def __init__(self, engine, separate_logger=False):
        # reference to the engine object
        self.engine = engine
        # if a logger is passed in it will overwrite the logger instance
        # if not then a new logger will be created
        self.logger = engine.logger if not separate_logger else Logger()

    @classmethod
    def classname(cls):
        return cls.__name__.lower()

    @classmethod
    def system_name(cls):
        return f"{cls.classname().replace('system', '')}_system"

    def process(self):
        raise NotImplementedError("Implement base system process method")
