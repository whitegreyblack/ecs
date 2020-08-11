# model.py

from dataclasses import dataclass as struct


@struct
class Point:
    x: int
    y: int
    @classmethod
    def origin(cls):
        return cls(x=0, y=0)

@struct
class Ruler:
    width: int
    height: int

@struct
class RenderContext:
    difficulty: int = 0
    x: int = 2
    y: int = 2

@struct
class GraphContext:
    nw: Point
    se: Point
    _origin: Point = None
    _dimensions: Ruler = None
    @property
    def dimensions(self) -> (int, int):
        if not self._dimensions:
            self._dimensions = Ruler(self.se.x - self.nw.x, self.se.y - self.nw.y)
        return self._dimensions
    @property
    def origin(self) -> Point:
        if not self._origin:
            self._origin = Point(self.se.x + self.nw.x, self.se.y + self.nw.y)
        return self._origin

