# command_move.py

"""Handles movement/collision"""
from source.common import join, join_drop_key
from source.ecs.components import Position, Destroyed, Collision, MeleeHitEffect


# helper functions
def check_for_floor_items(engine, position):
    items = []
    query = join(engine.items, engine.positions, engine.infos)
    for eid, (_, tile, info) in query:
        if position == tile:
            items.append(info.name)
    if items:
        if len(items) > 2:
            item_str = f"a {', a'.join(items[:len(items)-1])}, and a {items[-1]}"
        elif len(items) == 2:
            item_str = f"a {items[0]} and a {items[1]}"
        else:
            item_str = f"a {items[0]}"
        engine.logger.add(f"You step on {item_str}.")

def check_tile_info(engine, position):
    describeables = list()
    for p, i in join_drop_key(engine.positions, engine.infos):
        if (position.x == p.x and 
            position.y == p.y and 
            i.name is not 'floor'
        ):
            describeables.append(i.name)
    if describeables:
        engine.logger.add(', '.join(describeables))

def move(engine, entity, movement) -> bool:
    # if entity has no position component return early
    position = engine.positions.find(entity)
    if not position or not movement:
        return False

    # save temp positions for collision checking
    x, y = position.x + movement.x, position.y + movement.y

    # check map collisions
    tilemap = engine.tilemaps.find(eid=position.map_id)
    if not (0 <= x < tilemap.width and 0 <= y < tilemap.height):
        return collide(engine, entity, -1)

    # check unit collisions for specific movment types
    if position.movement_type == Position.MovementType.GROUND:
        # check unit collisions
        for entity_id, entity_position in engine.positions:
            if (entity_position.x == x and 
                entity_position.y == y and 
                entity_position.map_id == engine.world.id and 
                entity_id != entity and 
                entity_position.blocks_movement is True
            ):
                return collide(engine, entity, entity_id)

    if position.movement_type == Position.MovementType.VISIBLE:
        g = join_drop_key(engine.positions, engine.visibilities)
        for entity_position, visible in g:
            if (entity_position.x == x and
                entity_position.y == y and
                entity_position.map_id == engine.world.id and
                visible.level < 2
            ):
                return False

    # no collisions. move to the new position
    position.x += movement.x
    position.y += movement.y

    # check 
    if entity == engine.player:
        check_for_floor_items(engine, position)
    elif entity == engine.cursor:
        check_tile_info(engine, position)
        return False
    return True

def collide(engine, entity, other):
    # oob or environment collision. No logged message. Exit early
    if other == -1:
        return False
    is_player = entity == engine.player
    collidee = engine.infos.find(other)
    health = engine.healths.find(eid=other)
    if not health:
        if is_player:
            engine.logger.add(f'You walk into a {collidee.name}.')
        return False
    # process unit to unit collision
    collider = engine.infos.find(entity)
    # same species coexist
    if collider.name == collidee.name:
        return True
    return melee_attack(engine, entity, other)

def melee_attack(engine, entity, other):
    # attacker properties
    attacker = engine.infos.find(entity)
    equipment = engine.equipments.find(entity)

    # attackee properties
    attackee = engine.infos.find(other)
    health = engine.healths.find(other)
    armor = engine.armors.find(other)
    
    # damage calculations
    damage = 1
    if equipment and equipment.hand:
        weapon = engine.weapons.find(eid=equipment.hand)
        if weapon:
            damage = weapon.damage_swing

    # armor based reductions
    if armor:
        damage = max(0, damage - armor.defense)

    # final health loss
    health.cur_hp -= damage

    # record fight
    strings = []
    if entity == engine.player:
        strings.append(f"You attack the {attackee.name} for {damage} damage")
    else:
        strings.append(f"The {attacker.name} attacks the {attackee.name} for {damage} damage")
    if damage < 1:
        strings.append(f", but the attack did no damage!")
    else:
        strings.append(".")
    if health.cur_hp < 1:
        strings.append(f" The {attackee.name} dies.")
        engine.destroyed.add(other, Destroyed())
    else:
        # add a hit effect
        engine.effects.add(entity, MeleeHitEffect(other, '*', 0))
    engine.logger.add(''.join(strings))
    return True
