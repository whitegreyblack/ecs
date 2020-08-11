# room.py

import random
from dataclasses import dataclass as struct


class RoomNode:
    def __init__(self):
        _walls: set = None
        _floors: set = None
    def __repr__(self):
        return f"{self.__class__.__name__}"
    def walls(self):
        if not self._walls:
            self.generate_wall_points()
        return self.walls
    def generate_wall_points():
        raise NotImplementedError("Implement in inherited classes")
    def floors(self):
        if not self.floors:
            self.generate_floor_points()
        return self.floors
    def generate_floor_points():
        raise NotImplementedError("Implement in inherited classes")

class RectRoomNode(RoomNode):
    def __init__(self, width, height):
        super().__init__()
        self.width: int = width
        self.height: int = height
    def generate_wall_points(self):
        self._walls = set()
    def generate_floor_points(self):
        self._floors = set()

class CircleRoomNode(RoomNode):
    radius: int
    def generate_wall_points(self):
        self._walls = set()
    def generate_floor_points(self):
        self._floors = set()

class CrossRoomNode(RoomNode):
    width: int
    height: int
    def generate_wall_points(self):
        self._walls = set()
    def generate_floor_points(self):
        self._floors = set()

