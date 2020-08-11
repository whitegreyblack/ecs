# description.py

"""Provides info, render, and other shared/global entity properties"""

import enum
from source.maps import MapType

GOBLN_DESC = "A small creature easily defeatable but troublesome in a group."
SPEAR_DESC = "A basic weapon crafted from a long stick and a sharp rock."
FLOWR_DESC = "A small plant found in grass."
GOB_CORPSE = "The dead body of a goblin."
EDIBLE_ITEM = "Keeps you from starving."

# key: value
# name: (char, description, color, entity_type)
shared_cache: set = {
    # environment
    ('floor', '.', '', "grey"),
    ('bloodied floor', '*', '', "crimson"),
    ('wall', '#', '', "lighter grey"),
    ('opened door', '/', '', "orange"),
    ('closed door', '+', '', "orange"),
    ('down stairs', '>', '', None),
    ('up stairs', '<', '', None),
    ('grass', '.', '', (
        "darker grey",
        "darker sea",
        "darker green",
        "dark yellow",
        "#341d08"
        "#49b675"
    )),
    ('bloodied grass', '.', '', "crimson"),
    ('flower', "'", FLOWR_DESC, "yellow"),
    # ("tree", "T", '', "green"),
    # ("tree", "Y", '', "green"),

    # units
    ('goblin', 'g', GOBLN_DESC, ("chartreuse", "green", "lime")),
    ('goblin corpse', '%', GOB_CORPSE, ("green", "lime")),
    # 'rat': ('r', '', 95, UNIT),
    # 'bat': ('b', '', 233, UNIT),
    # 'villager': ('v', '', 0),

    # items
    ('spear', '/', SPEAR_DESC, "grey"),
    ('food', '%', EDIBLE_ITEM, "amber"),
}

SPELL_FIRE_BALL_DESC = "Throws a giant ball of fire at a location"
SPELL_CRYSTAL_NOVA_DESC = "Ice spikes burst from the earth towards a location"
spells = {
    # name(key) :: (mana cost, color, )
    'fireball': (5, '*', (167, 13, 125, 161, 89), SPELL_FIRE_BALL_DESC),
    'crystal nova': (3, '^', (46, 87, 160), SPELL_CRYSTAL_NOVA_DESC),
}

env_char_to_name = {
    '.': 'floor',
    '#': 'wall',
    '+': 'opened door',
    '/': 'closed door',
    '<': 'up stairs',
    '>': 'down stairs',
    "'": 'flower'
}

TILEMAPTYPES = {
    MapType.CAVE: {
        'walls': ["dark grey", "darker grey", "darkest grey"],
        'floors': ["lighter grey", "lightest grey", "grey", "white"]
    },
    MapType.TOWN: {
        'walls': [
            "#341d08",
            # "#1c0e02",
            # "#140d07"
        ], # brown walls
        'floors': ["green", "dark green", "darker green", "yellow"]
    }
}
