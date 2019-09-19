# event_system.py

"""Demo for event_system"""

import curses

from source.ecs.systems import system
from source.engine import Engine
from source.events import CommandEvent, TurnEvent
from source.keyboard import keyboard
from source.router import EventRouter


class TurnSystem(System):
    def process(self):
        ...


def create_engine(terminal):
    e = Engine(components=None
               systems=None,
               terminal=terminal,
               keyboard=keyboard
    )
    e.add_event_router(EventRouter())

def main(terminal):
    e = create_engine(terminal)
    e.run()

if __name__ == "__main__":
    curses.wrapper(main)
