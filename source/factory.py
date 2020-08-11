# factory.py

"""Factory methods to create new entities as json data"""

from source.ecs.components import (AI, Armor, Equipment, Health, Information,
                                   Input, Inventory, Item, Position, Render,
                                   Weapon)


def find_empty_space(engine):
    open_spaces = set()
    for entity_id, (tile, pos) in join(engine.tiles, engine.positions):
        if not pos.blocks:
            open_spaces.add((pos.x, pos.y))
    for entity_id, (hp, pos) in join(engine.healths, engine.positions):
        open_spaces.remove((pos.x, pos.y))
    for entity_id, (item, pos) in join(engine.items, engine.positions):
        open_spaces.remove((pos.x, pos.y))
    if not open_spaces:
        return None
    return open_spaces.pop()

def create_unit(engine, name):
    unit_data = dict()

    entity = engine.entities.create()
    engine.ais.add(entity, AI())
    engine.inputs.add(entity, Input(is_player=False))
    engine.infos.add(entity, Information(name))
    space = find_empty_space(engine)
    if not space:
        raise Exception("No empty space to place unit")
    engine.positions.add(entity, Position(*space))

    # unit specific attributes
    if name == 'rat':
        render = Render(char='r')
        health = Health(2, 2)
    elif name == 'goblin':
        render = Render(char='g', color="brown")
        health = Health(5, 5)
    elif name == 'bat':
        render = Render(char='b')
        health = Health(3, 3)

    engine.renders.add(entity, render)
    engine.healths.add(entity, health)

def create_player():
    player = engine.entities.create()
    engine.player = player
    engine.inputs.add(player, Input())
    if not spaces:
        raise Exception("No empty spaces to place player")
    space = spaces.pop()
    
    engine.positions.add(
        player, 
        Position(
            *space, 
            map_id=engine.world.id, 
            movement_type=Position.MovementType.GROUND
        )
    )
    engine.renders.add(player, Render('@'))
    engine.healths.add(player, Health(10, 20))
    engine.manas.add(player, Mana(10, 20))
    engine.infos.add(player, Information("Hero"))
    engine.inputs.add(player, Input(needs_input=True))

    # create armor for player
    # head
    helmet = engine.entities.create()
    engine.items.add(helmet, Item('armor', ('head',)))
    engine.renders.add(helmet, Render('['))
    engine.infos.add(
        helmet, 
        Information('iron helmet', 'Helps protect your head.')
    )
    engine.armors.add(helmet, Armor(2))
    # body
    platemail = engine.entities.create()
    engine.items.add(platemail, Item('armor', ('body',)))
    engine.renders.add(platemail, Render('['))
    engine.infos.add(
        platemail, 
        Information(
            'platemail', 
            'Armor made from sheets of metal. Heavy but durable.'
        )
    )
    engine.armors.add(platemail, Armor(5))
    # feet
    ironboots = engine.entities.create()
    engine.items.add(ironboots, Item('armor', ('feet',)))
    engine.renders.add(ironboots, Render('['))
    engine.infos.add(
        ironboots,
        Information('iron boots', 'Reinforced footwear.')
    )
    engine.armors.add(ironboots, Armor(3))

    # create a weapon for player
    spear = engine.entities.create()
    engine.items.add(spear, Item('weapon', ('hand', 'missiles')))
    engine.renders.add(spear, random.choice(engine.renders.shared['spear']))
    engine.infos.add(spear, engine.infos.shared['spear'])
    engine.weapons.add(spear, Weapon(4, 3))
    
    # create some missiles for player
    stone = engine.entities.create()
    engine.items.add(stone, Item('weapon', ('hand', 'missiles')))
    engine.renders.add(stone, Render('*'))
    engine.infos.add(stone, Information(
        'stone', 
        'A common item useful for throwing.'
    ))
    engine.weapons.add(stone, Weapon(1))

    # add created items to an equipment component
    e = Equipment(
        head=helmet,
        body=platemail,
        hand=spear, 
        feet=ironboots,
        missiles=stone
    )
    engine.equipments.add(player, e)
    
    # add an inventory
    i = Inventory()
    engine.inventories.add(player, Inventory())

