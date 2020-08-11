# move_system.py

"""
Move system controls unit movement.

Psuedocode:
If not oob || not wall blocked || not unit blocked
    if not friendly unit on block:
        move.x, move.y
    else:
        moving unit:
            move.x, move.y
        friendly unit:
            old.x, old.y
else:
    collision event
"""

import random

from source.common import join, join_drop_key
from source.ecs import (AI, Armor, Cursor, Decay, Equipment, HealEffect,
                        Health, Information, Input, Inventory, Item, Mana,
                        Movement, Position, Render, Spellbook, Weapon)

from .system import System


class MoveSystem(System):
    def on_move(self, event):
        """
            if out-of-bounds, environment or unit blocked:
                returns Collision result
            else:
                moves entity
        """
        self.logger.add(f"Move {self.engine.turns}")
        # if entity has no position component return early
        position = self.engine.positions.find(entity)
        if not position or not movement:
            return False

        # save temp positions for collision checking
        x, y = position.x + movement.x, position.y + movement.y

        # check map out-of-bounds collisions
        tilemap = self.engine.tilemaps.find(eid=position.map_id)
        if not (0 <= x < tilemap.width and 0 <= y < tilemap.height):
            return self.collide(entity, Collision(-1))

        # check unit collisions for specific movment types
        if position.movement_type == Position.MovementType.GROUND:
            # check unit collisions
            for entity_id, entity_position in self.engine.positions:
                if (entity_position.x == x and
                    entity_position.y == y and
                    entity_position.map_id == self.engine.world.id and
                    entity_id != entity and
                    entity_position.blocks is True
                ):
                    return self.collide(entity, Collision(entity_id))

        if position.movement_type == Position.MovementType.VISIBLE:
            g = join_drop_key(self.engine.positions, self.engine.visibilities)
            for entity_position, visible in g:
                if (entity_position.x == x and
                    entity_position.y == y and
                    entity_position.map_id == self.engine.world.id and
                    visible.level < 2
                ):
                    return False

        # no collisions. move to the new position
        position.x += movement.x
        position.y += movement.y

        # check 
        if entity == self.engine.player:
            self.check_for_floor_items(position)
        elif entity == self.engine.cursor:
            self.check_tile_info(position)
            return False
        return True
