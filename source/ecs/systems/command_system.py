# command_system.py

"""Refactor from input_system.py"""

import curses
import random
import time
from collections import defaultdict

from source.common import GameMode, diamond, join, join_drop_key, squares
from source.ecs.components import (Collision, Destroyed, Effect, Information,
                                   Item, MeleeHitEffect, Movement, Position,
                                   RangeHitEffect, Render, SpellEffect)
from source.ecs.systems.commands import (close_door, collide, go_down, go_up,
                                         melee_attack, move, open_door)
from source.ecs.systems.system import System
from source.keyboard import keypress_to_direction, movement_keypresses
from source.messenger import Logger
from source.pathfind import bresenhams, pathfind


class CommandSystem(System):

    def pick_item(self, entity):
        position = self.engine.positions.find(entity)
        g = join(
            self.engine.items,
            self.engine.positions,
            self.engine.infos
        )
        items = []
        items_picked_up = []
        for eid, (item, item_position, info) in g:
            if (position.x, position.y) == (item_position.x, item_position.y):
                items_picked_up.append(eid)
                items.append(info.name)
        if not items_picked_up:
            return False
        for item_id in items_picked_up:
            # remove from map
            self.engine.visibilities.remove(item_id)
            # self.engine.renders.remove(entity)
            self.engine.positions.remove(item_id)
            # add to inventory
            self.engine.router.route('inventory', 'add_item', entity, item_id)
        if len(items) > 2:
            item_str = f"a {', a '.join(items[:len(items)-1])}, and a {items[-1]}"
        elif len(items) == 2:
            item_str = f"a {items[0]} and a {items[1]}"
        else:
            item_str = f"a {items[0]}"
        self.engine.logger.add(f"You pick up {item_str}.")
        return True

    def missile(self, cursor):
        end = self.engine.positions.find(cursor)
        cursor_component = self.engine.cursors.find(cursor)
        start = self.engine.positions.find(cursor_component.entity)
        equipment = self.engine.equipments.find(cursor_component.entity)
        if equipment.missile_weapon and equipment.missiles:
            ...
        elif equipment.missiles:
            # save missiles item id
            missiles = equipment.missiles

            # remove stone from inventory
            unequipped = self.engine.router.route(
                'equipment',
                'unequip_item',
                cursor_component.entity,
                missiles
            )
            # processed correctly
            if unequipped:
                render = self.engine.renders.find(missiles)
                self.engine.logger.add(render.char)
                path = pathfind(self.engine, start, end, pathfinder=bresenhams)
                # add a position component to thrown item
                self.engine.positions.add(missiles, Position(
                    *path[-1], 
                    self.engine.world.id, 
                    movement_type=Position.MovementType.NONE,
                    blocks_movement=None
                ))
                # check if there is a unit in the path of the throw item
                # if there is one then calculate damage.
                # Do this by: 
                #     1. Getting all units in the missile path[1:]
                #        Note: this works since only one unit will be on a
                #              tile at any given time
                #     2 Check each position in the path against the unit
                #       positions. 
                #     3. If a unit exists then calculate chance to hit.
                #     4. If hit then calculate damage applied.
                units = {
                    (position.x, position.y): (uid, health)
                        for uid, (health, position) in join(
                            self.engine.healths, 
                            self.engine.positions
                        )
                        if (position.x, position.y) in path[1:]
                }
                # skip altogether if no units found in the unit query
                log = []
                is_player = cursor_component.entity == self.engine.player
                weapon = self.engine.infos.find(missiles)
                if units:
                    for p in path[1:]:
                        uid, health = units.get(p, (None, None))
                        if not uid:
                            continue
                        attacker = self.engine.infos.find(cursor_component.entity)
                        attack = self.engine.weapons.find(missiles).damage_throw
                        defender = self.engine.infos.find(uid)
                        if is_player:
                            log.append(f"You throw the {weapon.name} at {defender.name}")
                        else:
                            log.append(f"The {attacker.name} throws a {weapon.name} at {defender.name}")
                        # calculate chance to hit
                        # NOTE: calculate with a skill based chance later
                        # currently 50% chance to hit
                        if True:
                            armor = self.engine.router.route(
                                'armor',
                                'get_total_armor_value',
                                uid
                            )
                            damage = max(0, attack - armor)
                            health.cur_hp -= damage

                            if damage < 1:
                                log.append(f", but the missile did no damage!")
                            else:
                                log.append(f". It hits for {damage} damage.")
                            if health.cur_hp < 1:
                                log.append(f" The {defender.name} dies!")
                                self.engine.destroyed.add(uid, Destroyed())
                        else:
                            if is_player:
                                log.append(f", but miss!")
                            else:
                                log.append(f", but misses.")
                else:
                    if is_player:
                        log.append(f"You throw the {weapon.name} at nothing in particular.") 
                self.engine.logger.add(''.join(log))
                # add ranged hit effect to effect list
                effect = RangeHitEffect(cursor, render.char, '0', path)
                self.engine.effects.add(cursor_component.entity, effect)
        return True

    def cast_magic(self, cursor_id):
        cursor = self.engine.cursors.find(cursor_id)
        start = self.engine.positions.find(cursor.entity)
        end = self.engine.positions.find(cursor_id)
        spellname = self.engine.spells.shared[cursor.using]
        i = 0
        path = pathfind(self.engine, start, end, pathfinder=bresenhams)
        # TODO: this needs to be reduced from two lists to a zipped list
        flight_path = [
            (
                [(x, y),], 
                [random.choice(self.engine.renders.shared[spellname]),]
            )
            for x, y in path
        ]
        blast = (
            [(x+end.x, y+end.y) for x, y in diamond()],
            [
                random.choice(self.engine.renders.shared[spellname])
                    for _ in range(13)
            ]
        )
        flight_path.append(blast)
        for uid, (health, position) in join(
                self.engine.healths, 
                self.engine.positions):
            print(uid, position.x, position.y)        

        units = {
            (position.x, position.y): (uid, health)
                for uid, (health, position) in join(
                    self.engine.healths, 
                    self.engine.positions
                )
                if (position.x, position.y) in blast[0]
        }
        print(blast[0])
        print(units)
        # handle effects of spells
        blast_positions = []
        blast_colors = []
        if units:
            units_hit = []
            if spellname == "fireball":
                log = []
                for i, j in diamond():
                    x = i + end.x
                    y = j + end.y
                    blast_positions.append((x, y))
                    blast_colors.append(
                        random.choice(self.engine.renders.shared[spellname])
                    )
                    # just means no units are hit by the blast
                    if (x, y) not in units:
                        continue
                    damage = (2 - abs(i)) + (2 - abs(j)) + 1
                    log.append(f"{damage}")
                    units_hit.append((*units[(x, y)], damage))
                for uid, health, damage in units_hit:
                    info = self.engine.infos.find(uid)
                    health.cur_hp -= damage
                    log.append(f"The {info.name} was {'burned' if damage < 2 else 'scorched'} by fire. ({damage})")
                    if health.cur_hp < 1:
                        self.engine.destroyed.add(uid, Destroyed())
                        log.append(f"The {info.name} takes {damage} and dies!")
                    self.engine.logger.add(' '.join(log))
        else:
            self.engine.logger.add(f"You cast {spellname} at nothing in particular")
        effect = SpellEffect(cursor_id, flight_path)
        self.engine.effects.add(cursor.entity, effect)
        return True

    def able_to_target(self, entity: int) -> bool:
        eq = self.engine.equipments.find(entity)
        # most likely will not happen but handle anyways
        if not eq:
            self.engine.logger.add("You do not have any equipment on.")
        elif eq and not eq.missile_weapon:
            if eq.missiles:
                missiles = self.engine.weapons.find(eq.missiles)
                if not missiles.throw_requires_missile_weapon:
                    return True
            self.engine.logger.add("Cannot target without a missile weapon.")
        elif eq and not eq.missiles:
            self.engine.logger.add("Cannot target without any missile ammo.")
        else:
            return True
        return False

    def process(self, entity: int, command: str) -> bool:
        """
            Handles keypresses from keyboard
            Eventually would like this function to be called somewhat like:
                >>> self.actions[self.engine.mode][command](entity, command)
                or
                >>> self.actions[self.engine.mode][command](entity)
        """
        if command in movement_keypresses:
            return move(self.engine, entity, Movement.keypress_to_direction(command))
        elif command == 'escape':
            if self.engine.mode is not GameMode.NORMAL:
                self.engine.change_mode(GameMode.NORMAL)
            else:
                self.engine.change_screen('menuscreen')
        elif command == 'enter':
            if self.engine.mode == GameMode.NORMAL:
                return False
            if self.engine.mode == GameMode.MISSILE:
                t = self.missile(entity)
            elif self.engine.mode == GameMode.MAGIC:
                t = self.cast_magic(entity)
            self.engine.mode = GameMode.NORMAL
            return t
        elif command == 'i':
            self.engine.change_screen('inventoryscreen')
        elif command == 'e':
            self.engine.change_screen('equipmentscreen')
        elif command == 'tilde':
            if self.engine.mode == GameMode.NORMAL:
                self.engine.change_screen('spellscreen')
            elif self.engine.mode == GameMode.MAGIC:
                self.engine.change_mode(GameMode.NORMAL)
        elif command == 'l':
            if self.engine.mode == GameMode.LOOKING:
                self.engine.change_mode(GameMode.NORMAL)
            elif self.engine.mode == GameMode.NORMAL:
                self.engine.change_mode(GameMode.LOOKING)
        elif command == 'backtick':
            self.engine.change_mode(GameMode.DEBUG)
        elif command == 't':
            if self.engine.mode == GameMode.MISSILE:
                self.engine.change_mode(GameMode.NORMAL)
            if self.engine.mode == GameMode.NORMAL:
                if self.able_to_target(entity):
                    self.engine.change_mode(GameMode.MISSILE)
        elif command == 'greater-than':
            return go_down(self.engine, entity)
        elif command == 'less-than':
            return go_up(self.engine, entity)
        elif command == 'o':
            return open_door(self.engine, entity)
        elif command == 'c':
            return close_door(self.engine, entity)
        return False
