# term.py

"""Wrapper class for any terminal used (i.e. blt term, curses term, etc...)"""

class Terms(enum.Enum):
    blt = enum.auto()
    curses = enum.auto()

class Terminal:
    def __init__(self, term, term_type):
        self.__term = term
        self.__type = term_type
    def get_input(self):
        if self.__type == 0:
            raise NotImplementedError("differentiate between curses and blt")
        else:
            raise NotImplementedError("differentiate between curses and blt")
