# config.py

from dataclasses import dataclass


WIDTH, HEIGHT = 80, 24
MAX_ROOMS = (WIDTH * HEIGHT) // 2
DIFFICULTY_MULTIPLIER = [.025, .05, .1]
MAX_RETRY = 1000

@dataclass
class Direction:
    name: str
    x: int
    y: int

DIRECTIONS = [
    Direction('north', 0, 1),
    Direction('south', 0, -1),
    Direction('east', 1, 0),
    Direction('west', -1, 0)
]
