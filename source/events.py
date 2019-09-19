# events.py

"""Holds event dtos"""

from collections import namedtuple

class Event(object):
    def __repr__(self) -> str:
        attributes = [
            f"{s}={getattr(self, s)}"
                for s in self.__slots__
        ]
        attr_string = ", ".join(attributes)
        return f"{self.__class__.__name__}({attr_string})"

class TurnEvent(Event):
    __slots__ = ["entity_id", "turn_handler"]
    def __init__(self, entity_id, turn_handler):
        self.entity_id = entity_id
        self.turn_handler = turn_handler

class CommandEvent(Event):
    __slots__ = ["entity_id", "keypress", "command", "command_handler"]
    def __init__(self, entity_id, keypress, command):
        self.entity_id = entity_id
        self.keypress = keypress
        self.command = command
        self.command_handler = command_handler
