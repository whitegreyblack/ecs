# component.py

"""Component classes"""

import random
from dataclasses import dataclass, field
from source.keyboard import keypress_to_direction
from source.common import squares

@dataclass
class Component(object):
    """
    Base component class that defines subclass agnostic methods
    """
    __slots__ = []

    def __repr__(self):
        attributes = [ 
            f"{s}={getattr(self, s)}"
                for s in self.__slots__
                    if bool(hasattr(self, s) and getattr(self, s) is not None)
        ]
        attr_string = ", ".join(attributes)
        return f"{self.__class__.__name__}({attr_string})"

    @classmethod
    def classname(cls):
        return cls.__name__.lower()

@dataclass
class AI(Component):
    behavior: str = 'wander'
    path: list = None
    manager: str = 'ais'

@dataclass
class Collision(Component):
    entity_id: int = -1
    x: int = 0
    y: int = 0
    manager: str = 'collisions'

@dataclass
class Decay(Component):
    lifetime: int = 1000
    manager: str = 'decays'

@dataclass
class Destroy(Component):
    manager: str = 'destroyed'

@dataclass
class Effect(Component):
    char: str
    color: int
    ticks: int = 1
    manager: str = 'effects'

@dataclass
class Experience(Component):
    level: int = 1
    exp: int = 0
    manager: str = 'experiences'

@dataclass
class Health(Component):
    cur_hp: int = 1
    max_hp: int = 1
    manager: str = 'healths'
    @property
    def alive(self):
        return self.cur_hp > 0

@dataclass
class Input(Component):
    needs_input: bool = False
    manager: str = 'inputs'

@dataclass
class Energy(Component):
    amount: int
    full: int
    gain: int
    ready: bool
    manager: str = 'energies'

@dataclass
class Information(Component):
    name: str
    manager: str = 'infos'

@dataclass
class Movement(Component):
    x: int
    y: int
    manager: str = 'movements'
    @classmethod
    def keypress_to_direction(cls, keypress):
        return cls(*keypress_to_direction[keypress])
    @classmethod
    def random_move(cls, possible_spaces=None):
        if not possible_spaces:
            possible_spaces = [(x, y) for x, y in squares()]
        index = random.randint(0, len(possible_spaces) - 1)
        x, y = possible_spaces[index]
        return cls(x, y)

@dataclass
class Openable(Component):
    opened: bool = False
    manager: str = 'openables'

@dataclass
class Position(Component):
    x: int = 0
    y: int = 0
    map_id: int = -1
    moveable: bool = True
    blocks_movement: bool = True
    manager: str = 'positions'
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)
    def copy(
        self, 
        x=None, 
        y=None, 
        map_id=None, 
        moveable=None, 
        blocks_movement=None
    ):
        if x is None:
            x = self.x
        if y is None:
            y = self.y
        if map_id is None:
            map_id = self.map_id
        if moveable is None:
            moveable = self.moveable
        if blocks_movement is None:
            blocks_movement = self.blocks_movement
        return Position(x, y, map_id, moveable, blocks_movement)

@dataclass
class Render(Component):
    char: str = '@'
    depth: int = 0
    manager: str = 'renders'

@dataclass
class Tile(Component):
    # entity_id: int
    manager: str = 'tiles'

@dataclass
class TileMap(Component):
    width: int
    height: int
    manager: str = 'tilemaps'

@dataclass
class Visibility(Component):
    level: int = 0
    manager = 'visibilities'

@dataclass
class Inventory(Component):
    size: int = 10
    items: list = field(default_factory=list)
    manager = 'inventories'

@dataclass
class Item(Component):
    seen: bool = False
    manager = 'items'

@dataclass
class Unit(Component):
    manager = 'units'

components = Component.__subclasses__()

if __name__ == "__main__":
    from ecs.debug import dprint
    for component in Component.__subclasses__():
        try:
            print(component())
        except TypeError:
            pass
