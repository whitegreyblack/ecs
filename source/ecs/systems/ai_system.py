# ai_system.py

"""Refactor from input_system.py"""

import random
import time

from source.astar import pathfind
from source.common import (direction_to_keypress, eight_square, join,
                           join_conditional, nine_square, squares)
from source.ecs.components import (Collision, Information, Item, Movement,
                                   Render)
from source.ecs.systems.system import System
from source.keyboard import keypress_to_direction, movement_keypresses


class AISystem(System):
    def update(self):
        units = join(
            self.engine.healths,
            self.engine.positions,
            self.engine.infos,
            self.engine.ais
        )
        # start = time.time()
        tiles = {
            (p.x, p.y)
                for _, (p, v) in join(
                    self.engine.positions, 
                    self.engine.visibilities
                )
                if v.level > 1
        }
        # print('join:', time.time() - start)
        # start = time.time()
        # tiles = {
        #     (p.x, p.y)
        #         for _, (p, v) in join_conditional(
        #             self.engine.positions, 
        #             self.engine.visibilities,
        #             conditions=((1, lambda x: x.level > 1),)
        #         )
        # }
        # print('cond:', time.time() - start)
        # iterate all computers
        for eid, (h, p, i, ai) in units:
            player_visible = (p.x, p.y) in tiles
            if player_visible and ai.behavior != 'attack':
                ai.behavior = 'attack'
                # self.engine.logger.add(f"{i.name}({eid}) saw player and is moving to attack")
            elif player_visible and ai.behavior == 'attack':
                ai.path = None # overwrite path so it will be calculated on next run
                # self.engine.logger.add(f"{i.name}({eid}) lost player during chase")
            # player is not seen and monster was attacking but finished reaching path
            # if not v and ai.behavior == 'attack':
            #     # self.engine.logger.add(f"goblin moving towards {ai.path}")
            #     if not ai.path:
            #         # self.engine.logger.add(f"{i.name}({eid})({eid}) stopped attacking")
            #         ai.behavior = 'wander'
        self.engine.screen.render_logs_panel()

    def process(self, entity):
        """Computer commands currently only support mindless movement"""
        
        position = self.engine.positions.find(entity)
        # process as done if not in the current map
        if position.map_id != self.engine.world.id:
            return True
        info = self.engine.infos.find(entity)
        ai = self.engine.ais.find(entity)
        # simple ai logic (move, attack if enemy exists, run away)
        # behavior is updated during attack or update()
        movement = None
        while not movement:
            if ai.behavior == 'wander':
                # self.engine.logger.add(f"{info.name}({entity.id}) wanders around")
                movement = Movement.random_move()
            elif ai.behavior == 'attack':
                if ai.path:
                    path = ai.path.pop(0)
                    # self.engine.logger.add(f"{ai.path}, {path}")
                    movement = Movement(path[0] - position.x, path[1] - position.y)
                    # self.engine.logger.add(f"{info.name}({entity.id}) saw player and is moving to attack on last path")
                else:
                    target_position = self.engine.positions.find(self.engine.player)
                    # s = time.time()
                    ai.path = pathfind(self.engine, position, target_position)
                    # print(time.time() - s)
                    if not ai.path:
                        ai.behavior = 'wander'
                        # movement = Movement.random_move()
                        # self.engine.logger.add(f"{info.name}({entity.id}) was attacking player but lost sight of him")
                    # else:
                    #     path = ai.path.pop(0)
                    #     movement = Movement(path[0] - position.x, path[1] - position.y)
                        # self.engine.logger.add(f"{info.name}({entity.id}) saw player and is moving to attack on recalc path")
            elif ai.behavior == 'wait':
                movement = Movement(0, 0)
        return direction_to_keypress(movement.x, movement.y)
