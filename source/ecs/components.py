# component.py

""" `Component classes`

Notes:
    The current way components are constructed is that they have no reference
    to the entity id that they link to. This idea is that entity idea is not
    a necessary property for the component to 'know'. Entity id is only useful
    to the engine/component manager that holds all linkage//de-linkage between
    entities and components created. This creates a need for managers in the
    first place that monitor these components. For example:
    >>> e = EntityManager.create()  # creates a new id
    >>> i = Position(x, y)          # creates an position component
    >>> Position.add(e, i)          # link e to i. e also overwrites existing i

    However...if we provide the entity during component instantiation we can
    remove the managers and move all linkage functionality within a base class
    (most likely Component) and let the component types manage themselves.
    >>> Position(e, *args)
    or
    >>> Position(e, 1, 1) # should position take in an entity as a parameter?

    Internally it would call cls.components[e] = (return object from __new__)
    where components is a dictionary to map entity id to component.
    >>> Position.components
    {
        e: Position(*args),
    }
    But sometimes it does not look right as a parameter call. Should these
    components 'know' about their linked entity id? Allowing them to manage
    their own list of instances would allow global access using class
    attributes to those instances instead of creating managers inside the 
    engine. It is a possible alternate route to consider.
"""

import enum
import random
from dataclasses import dataclass, field

from source.common import squares
from source.keyboard import keypress_to_direction


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
    __slots__ = ['entity', 'x', 'x']
    manager: str = 'collisions'
    def __init__(self, entity: int = -1, x: int = 0, y: int = 0):
        self.entity = entity
        self.x = x
        self.y = y

class Decay(Component):
    __slots__ = ['lifetime']
    manager: str = 'decays'
    def __init__(self, lifetime:int=1000):
        self.lifetime = lifetime

class Destroyed(Component):
    __slots__ = []
    manager: str = 'destroyed'

class Effect(Component):
    __slots__ = []
    manager: str = 'effects'

class MeleeHitEffect(Effect):
    __slots__ = ['entity', 'char', 'color']
    def __init__(self, entity: int, char: str, color:int):
        self.entity = entity
        self.char = char
        self.color = color

class RangeHitEffect(Effect):
    __slots__ = ['entity', 'char', 'color', 'path']
    def __init__(self, entity: int, char: str, color: int, path: list):
        self.entity = entity
        self.char = char
        self.color = color
        self.path = path

class SpellEffect(Effect):
    __slots__ = ['entity', 'ticks']
    def __init__(self, entity, ticks):
        self.entity = entity
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
    __slots__ = "cur_hp max_hp tick_amount curr_amount full_amount".split()
    manager: str = 'healths'
    def __init__(
        self, 
        cur_hp: int = 1, 
        max_hp: int = 1, 
        tick_amount: int = 200, 
        full_amount: int = 10000,
        curr_amount: int = 0
    ):
        self.cur_hp = cur_hp
        self.max_hp = max_hp
        self.tick_amount = tick_amount
        self.full_amount = full_amount
        self.curr_amount = curr_amount

    @property
    def alive(self) -> bool:
        return self.cur_hp > 0

class Mana(Component):
    __slots__ = "cur_mp max_mp tick_amount curr_amount full_amount".split()
    manager: str = 'manas'
    def __init__(
        self,
        cur_mp: int = 1,
        max_mp: int = 1,
        tick_amount: int = 200,
        full_amount: int = 10000,
        curr_amount: int = 0
    ):
        self.cur_mp = cur_mp
        self.max_mp = max_mp
        self.tick_amount = tick_amount
        self.full_amount = full_amount
        self.curr_amount = curr_amount

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

class CurrentTurn(Component):
    __slots__ = ['finished']
    manager = 'current_turns'
    def __init__(self, finished=False):
        self.finished = finished

class Turn(Component):
    __slots__ = ['needs_turn', 'tick_amount', 'curr_amount', 'full_amount']
    manager = 'turns'
    def __init__(self,
                 tick_amount: int = 100,
                 full_amount: int = 1000,
                 curr_amount: int = 0):
        self.needs_turn = False
        self.tick_amount = tick_amount
        self.full_amount = full_amount
        self.curr_amount = curr_amount

class Openable(Component):
    __slots__ = ['opened']
    manager: str = 'openables'
    def __init__(self, opened: bool = False):
        self.opened = opened

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

class Position(Component):
    __slots__ = 'x', 'y', 'map_id', 'movement_type', 'blocks'
    manager: str = 'positions'
    class MovementType(enum.Enum):
        # no movement
        NONE = enum.auto()
        # only land tiles
        GROUND = enum.auto()
        # any tiles
        FLYING = enum.auto()
        # only water tiles
        SWIMMING = enum.auto()
        # cursor - only visible tiles
        VISIBLE = enum.auto()

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        map_id: int = -1,
        movement_type: int = MovementType.NONE,
        blocks: bool = True
    ):
        self.x = x
        self.y = y
        self.map_id = map_id
        self.movement_type = movement_type
        self.blocks = blocks
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)
    def copy(
        self,
        x: int = None,
        y: int = None,
        map_id: int = None,
        movement_type: int = None,
        blocks: bool = None
    ):
        return Position(
            x if x else self.x,
            y if y else self.y,
            map_id if map_id else self.map_id,
            movement_type if movement_type else self.movement_type,
            blocks if blocks is not None else self.blocks
        )

class Render(Component):
    __slots__ = ['char', 'color']
    manager: str = 'renders'
    def __init__(self, char: str = '@', color: int = 0):
        self.char = char
        self.color = color

class TileMapType(Component):
    __slots__ = ['walls', 'doors', 'floors', 'stairs']
    _walls = ["grey"]
    _floors = ["white"]
    _doors = ["orange"]
    _stairs = ["white"]
    manager = 'tilemaptypes'
    def __init__(self, walls=None, floors=None, doors=None, stairs=None):
        self.walls = walls or self._walls
        self.floors = floors or self._floors
        self.doors = doors or self._doors
        self.stairs = stairs or self._stairs

# singleton using nested classes
class Tile:
    class Tile(Component):
        __slots__ = []
        manager: str = 'tiles'
    instance = None
    def __new__(self):
        if not Tile.instance:
            Tile.instance = Tile.Tile()
        return Tile.instance

class TileMap(Component):
    __slots__ = 'width height map_type'.split()
    manager: str = 'tilemaps'
    def __init__(self, width: int, height: int, map_type='cave'):
        self.width = width
        self.height = height
        self.map_type = map_type

class Visibility(Component):
    __slots__ = ['level']
    manager: str = 'visibilities'
    def __init__(self, level: int = 0):
        self.level = level

class Inventory(Component):
    __slots__ = ['size', 'items']
    manager: str = 'inventories'
    categories = [
        'weapon', 
        'helmets',
        'armor',
        'footwear',
        'general', 
        'food', 
        'crafting', 
        'other'
    ]
    def __init__(self, size: int = 10, items: list = None):
        self.size = size
        self.items = items if items else list()

class Equipment(Component):
    equipment = __slots__ = [
        "head",
        "body",
        "hand",
        "feet",
        "missile_weapon",
        "missiles"
    ]
    manager: str = 'equipments'
    def __init__(
        self,
        head: int = None,
        body: int = None,
        hand: int = None,
        feet: int = None,
        missile_weapon: int = None,
        missiles: int = None
    ):
        self.head = head
        self.body = body
        self.hand = hand
        self.feet = feet
        self.missile_weapon = missile_weapon
        self.missiles = missiles

class Spellbook(Component):
    __slots__ = ['spells']
    manager: str = 'spellbooks'
    def __init__(self, spells=None):
        self.spells = spells if spells else list()

class Spell(Component):
    __slots__ = ['mana_cost']
    manager: str = 'spells'
    identify: dict = dict()
    def __init__(self, mana_cost):
        self.mana_cost = mana_cost

class Weapon(Component):
    __slots__ = ['damage']
    manager: str = 'weapons'
    def __init__(
        self, 
        damage_swing: int = 1, 
        damage_throw: int = 1,
        throw_requires_weapon: bool = False
    ):
        self.damage_swing = damage_swing
        self.damage_throw = damage_throw
        self.throw_requires_missile_weapon = False

class HealEffect:
    """
        Item sub component -- shouldn't inherit from component
    """
    __slots__ = ['heal_amount']
    def __init__(self, heal_amount: int = 0):
        self.heal_amount = heal_amount

class Item(Component):
    __slots__ = ['category', 'equipment_type', 'effect']
    manager: str = 'items'
    def __init__(
        self,
        category: str = 'general',
        eqtype: list = None,
        effect: object = None
    ):
        self.category = category
        self.equipment_types = eqtype
        self.effect = effect

class Armor(Component):
    __slots__ = ['defense']
    manager: str = 'armors'
    def __init__(self, defense: int = 0):
        self.defense = defense

class Cursor(Component):
    __slots__ = ['entity', 'using']
    manager: str = 'cursors'
    def __init__(self, entity: int):
        self.entity = entity
        self.using = -1

class StatusType(enum.Enum):
    BURNING = enum.auto()
    FROZEN = enum.auto()
    BLEEDING = enum.auto()
    POISONED = enum.auto()

class Status(Component):
    __slots__ = ['status', 'color']
    manager: str = 'statuses'
    def __init__(self, status: int):
        self.status = status
        if self.status == StatusType.BURNING:
            self.color = 0
        elif self.status == StatusType.FROZEN:
            self.color = 0

# export all component types
components = Component.__subclasses__()

if __name__ == "__main__":
    from ecs.debug import dprint
    for component in Component.__subclasses__():
        try:
            print(component())
        except TypeError:
            pass
