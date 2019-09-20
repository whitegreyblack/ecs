# spawn_system.py

"""Spawn system controls unit and item generation"""

import random

from source.common import join, join_drop_key
from source.ecs import (AI, Armor, Cursor, Decay, Equipment, HealEffect, Spell, 
                        Health, Information, Input, Inventory, Item, Mana,
                        Position, Render, Spellbook, Weapon)

from .system import System


class SpawnSystem(System):
    def __init__(self, engine, logger=None):
        super().__init__(engine, logger)
        # TODO: move to a new spawn Component attached to the tilemap
        self.respawn_rate = 50
        self.current_tick = self.respawn_rate

    def find_valid_spaces(self) -> list:
        return [
            (position.x, position.y)
                for _, position, visible in join_drop_key(
                    self.engine.tiles, 
                    self.engine.positions, 
                    self.engine.visibilities
                )
                if visible.level < 2 and not position.blocks_movement
        ]

    def find_empty_spaces(self):
        return [
            (position.x, position.y)
                for _, position in join_drop_key(
                    self.engine.tiles, 
                    self.engine.positions
                )
                if not position.blocks_movement
        ]

    def find_unlit_spaces(self):
        g = join_drop_key(self.engine.tiles, self.engine.positions)
        return {
            (position.x, position.y)
                for (_, position, visible) in join_drop_key(
                    self.engine.tiles,
                    self.engine.positions,
                    self.engine.visibilities
                )
                if visible.level > 1
                    and not position.blocks_movement
        }
    
    def spawn_player(self, space):
        player = self.engine.entities.create()
        # add components
        self.engine.inputs.add(player, Input())
        self.engine.positions.add(
            player, 
            Position(
                *space, 
                map_id=self.engine.world.id, 
                movement_type=Position.MovementType.GROUND
            )
        )
        self.engine.renders.add(player, Render('@'))
        self.engine.healths.add(player, Health(10, 20))
        self.engine.manas.add(player, Mana(10, 20))
        self.engine.infos.add(player, Information("Hero"))
        self.engine.inputs.add(player, Input(needs_input=True))

        # create armor items for player to equip
        # head
        helmet = self.engine.entities.create()
        self.engine.items.add(helmet, Item('armor', ('head',)))
        self.engine.renders.add(helmet, Render('['))
        self.engine.infos.add(
            helmet, 
            Information('iron helmet', 'Helps protect your head.')
        )
        self.engine.armors.add(helmet, Armor(2))
        # body
        platemail = self.engine.entities.create()
        self.engine.items.add(platemail, Item('armor', ('body',)))
        self.engine.renders.add(platemail, Render('['))
        self.engine.infos.add(
            platemail, 
            Information(
                'platemail', 
                'Armor made from sheets of metal. Heavy but durable.'
            )
        )
        self.engine.armors.add(platemail, Armor(5))
        # feet
        ironboots = self.engine.entities.create()
        self.engine.items.add(ironboots, Item('armor', ('feet',)))
        self.engine.renders.add(ironboots, Render('['))
        self.engine.infos.add(ironboots, Information('iron boots', 'Reinforced footwear.'))
        self.engine.armors.add(ironboots, Armor(3))

        # create a weapon for player
        spear = self.engine.entities.create()
        self.engine.items.add(spear, Item('weapon', ('hand', 'missiles')))
        self.engine.renders.add(spear, random.choice(self.engine.renders.shared['spear']))
        self.engine.infos.add(spear, self.engine.infos.shared['spear'])
        self.engine.weapons.add(spear, Weapon(4, 3))
        
        # create some missiles for player
        stone = self.engine.entities.create()
        self.engine.items.add(stone, Item('weapon', ('hand', 'missiles')))
        self.engine.renders.add(stone, Render('*'))
        self.engine.infos.add(stone, Information(
            'stone', 
            'A common item useful for throwing.'
        ))
        self.engine.weapons.add(stone, Weapon(1))

        # add created items to an equipment component
        e = Equipment(
            head=helmet,
            body=platemail,
            hand=spear, 
            feet=ironboots,
            missiles=stone
        )
        self.engine.equipments.add(player, e)
        
        # add an inventory
        i = Inventory()
        self.engine.inventories.add(player, Inventory())

        # add a spellbook with a spell
        spellbook = Spellbook(spells=[0, 1])
        self.engine.spellbooks.add(player, spellbook)
        return player

    def spawn_cursor(self, entity):
        cursor = self.engine.entities.create()
        self.engine.cursors.add(cursor, Cursor(entity))
        self.engine.positions.add(cursor, Position(blocks_movement=False))
        return cursor

    def spawn_unit(self, space):
        # create unit entity
        computer = self.engine.entities.create()
        self.engine.inputs.add(computer, Input())
        self.engine.positions.add(
            computer,
            Position(
                *space, 
                map_id=self.engine.world.id,
                movement_type=Position.MovementType.GROUND
            )
        )
        self.engine.ais.add(computer, AI())
        render = random.choice(self.engine.renders.shared['goblin'])
        self.engine.renders.add(computer, render)
        info = self.engine.infos.shared['goblin']
        self.engine.infos.add(computer, info)
        self.engine.healths.add(computer, Health(2, 2))
        
        # add items to inventory
        item = self.engine.entities.create()
        self.engine.items.add(item, Item('weapon', ('hand', 'missile')))
        r = random.choice(self.engine.renders.shared['spear'])
        self.engine.renders.add(item, r)
        self.engine.infos.add(item, self.engine.infos.shared['spear'])
        self.engine.inventories.add(computer, Inventory(items=[item]))

    def spawn_item(self, space):
        item = self.engine.entities.create()
        self.engine.positions.add(item, Position(
            *space, 
            map_id=self.engine.world.id, 
            movement_type=Position.MovementType.NONE, 
            blocks_movement=False
        ))
        r = random.choice(self.engine.renders.shared['food'])
        self.engine.renders.add(item, r)
        self.engine.infos.add(item, self.engine.infos.shared['food'])
        self.engine.items.add(item, Item('food', effect=HealEffect(3)))
        self.engine.decays.add(item, Decay())
        return item
    
    def process(self):
        units = [
            (eid, health, position)
                for eid, (health, position) in join(
                    self.engine.healths,
                    self.engine.positions
                )
                if position.map_id == self.engine.world.id
                    and eid != self.engine.player
        ]
        if len(units) < 3:
            if self.current_tick < 0:
                self.current_tick = self.respawn_rate
            # self.engine.logger.add(self.current_tick)
            self.current_tick -= 1
            if self.current_tick == 0:
                spaces = self.find_valid_spaces()
                # probably wouldn't happen but if it does then exit early
                if not spaces:
                    return
                random.shuffle(spaces)
                space = spaces.pop()
                self.spawn_unit(space)
