# spell_system.py

"""spell system controls unit and item generation"""

import random

from source.common import join, join_drop_key
from source.ecs import (AI, Armor, Cursor, Decay, Equipment, HealEffect, Spell, 
                        Health, Information, Input, Inventory, Item, Mana,
                        Position, Render, Spellbook, Weapon)

from .system import System


class SpellSystem(System):
    ...