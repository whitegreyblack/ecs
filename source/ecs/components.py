# component.py

"""Component classes"""

import random
from dataclasses import dataclass, field
from source.keyboard import keypress_to_direction
from source.common import squares

class Component(object):
    """
    Base component class that defines subclass agnostic methods
    """
    def __repr__(self) -> str:
        attributes = [
            f"{s}={getattr(self, s)}"
                for s in self.__slots__
        ]
        attr_string = ", ".join(attributes)
        return f"{self.__class__.__name__}({attr_string})"

    @classmethod
    def classname(cls) -> str:
        return cls.__name__.lower()

class AI(Component):
    __slots__ = ['behavior', 'path']
    manager: str = 'ais'
    def __init__(self, behavior: str = 'wander'):
        self.behavior = behavior
        self.path = None
    
class Collision(Component):
    __slots__ = ['entity_id', 'x', 'x']
    manager: str = 'collisions'
    def __init__(self, entity_id: int = -1, x: int = 0, y: int = 0):
        self.entity_id = entity_id
        self.x = x
        self.y = y

class Decay(Component):
    __slots__ = ['lifetime']
    manager: str = 'decays'
    def __init__(self, lifetime:int=1000):
        self.lifetime = lifetime

# class Destroy(Component):
#     __slots__ = []
#     manager: str = 'destroyed'

class Effect(Component):
    __slots__ = ['entity_id', 'char', 'color', 'ticks']
    manager: str = 'effects'
    def __init__(self, entity_id:int, char:str, color:int, ticks:int=1):
        self.entity_id = entity_id
        self.char = char
        self.color = color
        self.ticks = ticks

# class Energy(Component):
#     amount: int
#     full: int
#     gain: int
#     ready: bool
#     manager: str = 'energies'

# @dataclass
# class Experience(Component):
#     level: int = 1
#     exp: int = 0
#     manager: str = 'experiences'

class Health(Component):
    __slots__ = ['cur_hp', 'max_hp', 'heal_tick', 'heal_curr', 'heal_full']
    manager: str = 'healths'
    def __init__(
        self, 
        cur_hp: int=1, 
        max_hp: int=1, 
        heal_tick: int=200, 
        heal_full: int=10000
    ):
        self.cur_hp = cur_hp
        self.max_hp = max_hp
        self.heal_tick = heal_tick
        self.heal_full = heal_full
        self.heal_curr = 0

    @property
    def alive(self) -> bool:
        return self.cur_hp > 0

class Information(Component):
    __slots__ = ['name', 'description']
    manager: str = 'infos'
    def __init__(self, name: str, description: str = None):
        self.name = name
        self.description = description

class Input(Component):
    __slots__ = ['needs_input']
    manager: str = 'inputs'
    def __init__(self, needs_input: bool = False):
        self.needs_input = needs_input

class Movement(Component):
    __slots__ = ['x', 'y']
    manager: str = 'movements'
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
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

class Openable(Component):
    __slots__ = ['opened']
    manager: str = 'openables'
    def __init__(self, opened: bool = False):
        self.opened = opened

class Position(Component):
    __slots__ = ['x', 'y', 'map_id', 'moveable', 'blocks_movement']
    manager: str = 'positions'
    def __init__(self, 
        x: int = 0,
        y: int = 0,
        map_id: int = -1,
        moveable: bool = True,
        blocks_movement: bool = True
    ):
        self.x = x
        self.y = y
        self.map_id = map_id
        self.moveable = moveable
        self.blocks_movement = blocks_movement
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)
    def copy(
        self,
        x: int = None, 
        y: int = None, 
        map_id: int = None, 
        moveable: bool = None, 
        blocks_movement: bool = None
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

class Render(Component):
    __slots__ = ['char']
    manager: str = 'renders'
    def __init__(self, char: str = '@'):
        self.char = char

class Tile(Component):
    __slots__ = []
    manager: str = 'tiles'

class TileMap(Component):
    __slots__ = ['width', 'height']
    manager: str = 'tilemaps'
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

class Visibility(Component):
    __slots__ = ['level']
    manager: str = 'visibilities'
    def __init__(self, level: int = 0):
        self.level = level

class Inventory(Component):
    __slots__ = ['size', 'items', 'categories']
    manager: str = 'inventories'
    def __init__(self, size: int = 10, items: list = None):
        self.size = size
        self.items = items if items else list()
        self.categories = [
            'weapon', 
            'general', 
            'food', 
            'crafting', 
            'other'
        ]

class Equipment(Component):
    __slots__ = ['head', 'body', 'hand', 'feet']
    manager: str = 'equipments'
    def __init__(
        self, 
        head: int = None,
        body: int = None,
        hand: int = None,
        feet: int = None
    ):
        self.head = head
        self.body = body
        self.hand = hand
        self.feet = feet

class Weapon(Component):
    __slots__ = ['damage']
    manager: str = 'weapons'
    def __init__(self, damage: int = 0):
        self.damage = damage

class Item(Component):
    __slots__ = ['category', 'seen']
    manager: str = 'items'
    def __init__(self, category: str = 'general'):
        self.category = category
        self.seen = False

# class Unit(Component):
#     race: str
#     manager: str = 'units'

class Armor(Component):
    __slots__ = ['defense']
    manager: str = 'armors'
    def __init__(self, defense: int = 0):
        self.defense = defense

components = Component.__subclasses__()

if __name__ == "__main__":
    from ecs.debug import dprint
    for component in Component.__subclasses__():
        try:
            print(component())
        except TypeError:
            pass
