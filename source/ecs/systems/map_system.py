# map_system

""" `Map system`

Map system is not called every turn but only on map change events

TileMap to Tiles:
    Each tilemap is assigned an entity id. The tilemap entity id is used as a
    key in each tile of the map. Each tile is referenced in an N number of
    components which relate to the tile. They are found using the tile entity 
    id.
            +---------+    +------+    +-------------+
            | TileMap | -> | Tile | -> | Component 1 |
            +---------+    +------+    +-------------+
                            :                ...
                            :          +-------------+
                            + - - - -> | Component N |
                                       +-------------+

Tiles:
    TileID        -> instance (int)
    Tile          -> singleton (maybe enum(int))
    Position      -> instance
    Visibility    -> instance
    Render        -> instance
    Information   -> shared
    Openable      -> instance
"""

import pickle
import random

from source.common import join
from source.description import env_char_to_name
from source.ecs.components import (Information, Item, Openable, Position,
                                   Render, Tile, TileMap, Visibility)
from source.generate import (add_boundry_to_matrix, array_to_matrix,
                             build_cave, cell_auto, dimensions, flood_fill,
                             generate_poisson_array, matrix,
                             replace_cell_with_stairs, string)
from source.graph import DungeonNode, WorldGraph

from .system import System


class MapSystem(System):
    def save_map(self, map_id):
        tilemap = self.engine.tilemaps.find(eid=map_id)
        tiles = {}
        for eid, tile in self.engine.tiles:
            group = [tile]
            group.append(self.engine.positions.find(eid=eid))
            group.append(self.engine.renders.find(eid=eid))
            group.append(self.engine.infos.find(eid=eid))
            group.append(self.engine.visibilities.find(eid=eid))
            openable = self.engine.openables.find(eid=eid)
            if openable:
                group.append(openable)
            tiles[eid] = group
        with open(f'saves/map_{map_id}.pickle', 'wb') as f:
            pickle.dump(tilemap, f, pickle.HIGHEST_PROTOCOL)
            pickle.dump(tiles, f, pickle.HIGHEST_PROTOCOL)
    
    def load_map(self, map_id):
        with open(f'saves/map_{map_id}.pickle', 'rb') as f:
            tilemap = pickle.load(f)
            tileinfo = pickle.load(f)
        self.engine.tilemaps.add(map_id, tilemap)
        for tile, components in tileinfo.items():
            for component in components:
                getattr(self.engine, component.manager).add(tile, component)

    def delete_map(self, map_id):
        # clear dictionaries to improve speedup
        self.engine.tilemaps.remove(eid=map_id)
        for eid, tile in self.engine.tiles:
            self.engine.positions.remove(eid=eid)
            self.engine.renders.remove(eid=eid)
            self.engine.infos.remove(eid=eid)
        self.engine.visibilities.components.clear()
        self.engine.openables.components.clear()
        self.engine.tiles.components.clear()

    def build_map(self, map_type, map_string) -> (object, object):
        """
            Width x Height is determined by map_string dimensions if it exists.
            Otherwise, a random map is generated and used instead.

            Currently, predetermined levels are town maps only.
            Empty map strings leads to the construction of cave maps.
        """
        # if given a specific map string use it instead of a random map
        if map_string:
            dungeon = [ [ c for c in row ] for row in map_string.split('\n') ]
            width, height = dimensions(dungeon)
            tilemap = TileMap(width, height, map_type)
            # add environmental details (grass, flowers) if town
            if map_type == "town":
                matrix = array_to_matrix(
                    generate_poisson_array(width, height),
                    width, height,
                    filter=lambda x: x < 3 or x >= 8,
                    chars=("'", ".")
                )
                for y in range(len(dungeon)):
                    for x in range(len(dungeon[0])):
                        if dungeon[y][x] == '.':
                            dungeon[y][x] = matrix[y][x]
        else:
            w, h = 58, 17
            tilemap = TileMap(w, h, map_type)
            random_array = generate_poisson_array(w, h)
            no_stairs = array_to_matrix(
                random_array,
                w, h,
                filter=lambda x: x < 3 or x >= 8
            )
            no_stairs = add_boundry_to_matrix(no_stairs, bounds=1)
            for i in range(4):
                no_stairs = cell_auto(no_stairs, deadlimit=5+(i-5))
            no_stairs = flood_fill(no_stairs)
            dungeon = replace_cell_with_stairs(no_stairs)
            print(string(dungeon))
        return tilemap, dungeon

    def convert_dungeon_to_ecs(self, map_id, map_type, dungeon):
        # add tiles and tile specific attribute components
        maptype = self.engine.tilemaptypes.shared[map_type]
        environment = ".#+/'"
        blocked = environment[1:3]
        doors = environment[2:4]
        for y, row in enumerate(dungeon):
            for x, char in enumerate(row):
                if char == ' ':
                    continue
                # shared components
                tile_id = self.engine.entities.create()
                # tile
                self.engine.tiles.add(tile_id, Tile())
                # visibility
                self.engine.visibilities.add(tile_id, Visibility())
                # position
                self.engine.positions.add(tile_id, Position(
                    x, y,
                    map_id=map_id,
                    movement_type=Position.MovementType.NONE,
                    blocks=char in blocked
                ))
                # info
                info = self.engine.infos.shared[env_char_to_name[char]]
                self.engine.infos.add(tile_id, info)
                # render
                if char in ".'":
                    colors = maptype.floors
                elif char == '#':
                    colors = maptype.walls
                elif char in doors:
                    colors = maptype.doors
                else:
                    colors = maptype.stairs
                render = Render(char, random.choice(colors))
                self.engine.renders.add(tile_id, render)
                # openable
                if char in doors:
                    # This is a unique case (possibly more in the future) in
                    # that this tile creates a map entity with Openable.
                    openable = Openable(opened=char=='/')
                    self.engine.openables.add(tile_id, openable)
                # elif c == "'" and random.randint(0, 3) == 0:
                #     # This is a unique case (possibly more in the future) in
                #     # that this tile creates both a map and item entity:
                #     flower = self.engine.entities.create()
                #     self.engine.items.add(flower, Item('crafting'))
                #     self.engine.positions.add(flower, Position(
                #         x, y,
                #         map_id=map_id,
                #         movement_type=Position.MovementType.NONE,
                #         blocks=False
                #     ))
                #     r = random.choice(self.engine.renders.shared['flower'])
                #     self.engine.renders.add(flower, r)
                #     self.engine.infos.add(
                #         flower,
                #         self.engine.infos.shared['flower']
                #     )

    def add_map_to_world(self, map_id):
        # create world graph if ran the first time
        if not self.engine.world:
            self.engine.world = WorldGraph({
                map_id: DungeonNode(map_id)
            }, map_id)
        # update current map to save parent/child relationship
        else:
            self.engine.world.node.child_id = map_id
            current_map_id = self.engine.world.id
            self.engine.world.update({
                map_id: DungeonNode(
                    map_id,
                    parent_id=current_map_id
                )
            })

    def generate_map(self, map_type, map_string=None):
        # clear dictionaries to improve speedup
        if self.engine.world:
            self.save_map(self.engine.world.id)
            self.delete_map(self.engine.world.id)
        map_id = self.engine.entities.create()
        # get map info component and map geography
        tilemapinfo, dungeon = self.build_map(map_type, map_string)
        self.engine.tilemaps.add(map_id, tilemapinfo)
        self.convert_dungeon_to_ecs(map_id, map_type, dungeon)
        self.add_map_to_world(map_id)

    def regenerate_map(self, map_id):
        """
            Wrapper for load_map. Saves current map if it exists before reading
            saved map data
        """
        if self.engine.world:
            self.save_map(map_id)
            self.delete_map(map_id)
        self.load_map(self.engine.world.id)
