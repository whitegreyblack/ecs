# description.py

"""Provides info, render, and other shared/global entity properties"""


GOBLN_DESC = "A small creature easily defeatable but troublesome in a group."
SPEAR_DESC = "A basic weapon crafted from a long stick and a sharp rock."
FLOWR_DESC = "A small plant found in grass."
GOB_CORPSE = "The dead body of a goblin."
EDIBL_ITEM = "Keeps you from starving."

TYPE_DEFAULT_ENVIRON = 1
TYPE_ALTERED_ENVIRON = 2
TYPE_WEAPON = 3
TYPE_ITEM = 4
TYPE_UNIT = 5
TYPE_SPELL = 6

# key: value
# name: (char, description, color, entity_type)
shared_cache = {
    # environment
    'floor': ('.', '', 102, TYPE_DEFAULT_ENVIRON),
    'bloodied floor': ('*', '', 89, TYPE_ALTERED_ENVIRON),
    'wall': ('#', '', 95, TYPE_DEFAULT_ENVIRON),
    'opened wooden door': ('/', '', 131, TYPE_DEFAULT_ENVIRON),
    'closed wooden door': ('+', '', 131, TYPE_DEFAULT_ENVIRON),
    # 'metal door': ('+', '', 151),
    # 'metal door': ('/', '', 151),
    'down stairs': ('>', '', 0, TYPE_DEFAULT_ENVIRON),
    'up stairs': ('<', '', 0, TYPE_DEFAULT_ENVIRON),
    'grass': ('"', '', (71, 47), TYPE_DEFAULT_ENVIRON),
    'bloodied grass': ('"', '', 89, TYPE_ALTERED_ENVIRON),
    # units
    'goblin': ('g', GOBLN_DESC, (83, 47), TYPE_UNIT),
    'goblin corpse': ('%', GOB_CORPSE, (83, 47), TYPE_ITEM),
    # 'rat': ('r', '', 95, TYPE_UNIT),
    # 'bat': ('b', '', 233, TYPE_UNIT),
    # 'villager': ('v', '', 0),
    # items
    'spear': ('/', SPEAR_DESC, 253, TYPE_WEAPON),
    'food': ('%', EDIBL_ITEM, 167, TYPE_ITEM),
    'flower': (';', FLOWR_DESC, 227, TYPE_ITEM)
}

SPELL_FIRE_BALL = "Throws a giant ball of fire at a location"
SPELL_CRYSTAL_NOVA = "Ice spikes burst from the earth towards a location"
spells = {
    # name(key) :: (mana cost, color, )
    'fireball': (5, '*', (167, 13, 125, 161, 89), SPELL_FIRE_BALL),
    'crystal nova': (3, '^', (46, 87, 160), SPELL_CRYSTAL_NOVA),
}

env_char_to_name = {
    char: name
        for name, (char, _, _, idtype) in shared_cache.items()
            if idtype == TYPE_DEFAULT_ENVIRON
}
