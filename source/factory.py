# factory.py

"""Factory methods to create new entities as json data"""

from source.ecs.components import (AI, Health, Information, Input, Position,
                                   Render)

def find_empty_space(engine):
    open_spaces = set()
    for entity_id, (tile, pos) in join(engine.tiles, engine.positions):
        if not pos.blocks_movement:
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
        render = Render(char='g')
        health = Health(5, 5)
    elif name == 'bat':
        render = Render(char='b')
        health = Health(3, 3)

    engine.renders.add(entity, render)
    engine.healths.add(entity, health)
