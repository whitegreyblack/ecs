# generate.py

"""Holds functions for map generation"""

import math
import random
from copy import deepcopy

import numpy as np

from source.common import cardinal, squares
from source.graph import create_mst


class MapGenerator:
    def __init__(self, data):
        self.data = data
    @property
    def width(self):
        return len(self.data[0])
    @property
    def height(self):
        return len(self.data)
    @classmethod
    def poisson(cls, width, height, filterpoint=5):
        array = np.random.poisson(5, width * height)
        matrix = [['.' for _ in range(width)] for _ in range(height)]
        for i in range(width):
            for j in range(height):
                if array[j * width + i] == filterpoint:
                    matrix[j][i] = '#'
        return cls(matrix)
    def bounded(self):
        for i in (0, 1, self.width-2, self.width-1):
            for j in range(self.height):
                self.data[j][i] = '#'
        for j in (0, 1, self.height-2, self.height-1):
            for i in range(self.width):
                self.data[j][i] = '#'
        return self
    def stringify(self):
        return  '\n'.join(''.join(row) for row in self.data)

def dimensions(matrix: list) -> tuple:
    return len(matrix[0]), len(matrix)

def matrix(string: str) -> list:
    return [list(row) for row in string.split('\n')]

def string(matrix: list) -> str:
    return '\n'.join(''.join(str(s) for s in row) for row in matrix)

def empty_matrix(width: int, height: int, char: chr='.') -> list:
    return [list(char * width) for h in range(height)]

def empty_mapstring(width: int, height: int, char: chr='.') -> str:
    return string(empty_matrix(width, height, char))

def empty_room(width: int, height: int) -> list:
    return [
        ('#' * width)
            if h in (0, height - 1) else (f"#{'.' * (width - 2)}#")
                for h in range(height)
    ]

def rotate_string(mapstring: str) -> str:
    '''string -> matrix -> rotate() -> matrix -> string'''
    return string(rotate(matrix(mapstring)))

def rotate(matrix: list) -> list:
    width, height = dimensions(matrix)
    arr = empty_matrix(height, width)
    for y in range(height):
        for x in range(width):
            try:
                c = matrix[y][x]
            except:
                raise Exception("outer", x, y)
            else:
                try:
                    arr[x][y] = c
                except:
                    raise Exception("inner", x, y)
    return arr

def center_mapstring(old: list, new: list) -> list:
    new_width, new_height = len(new[0]), len(new)
    old_width, old_height = len(old[0]), len(old)

    xoffset = (new_width - old_width) // 2
    yoffset = (new_height - old_height) // 2

    for y in range(old_height):
        for x in range(old_width):
            if old[y][x] == '.':
                continue
            new[y+yoffset][x+xoffset] = old[y][x]
    return new

def extend(mapstring: str, mapgen: object=empty_matrix, char: str='"') -> str:
    old = matrix(mapstring)
    new = mapgen(60, 17, char)
    new = center_mapstring(old, new)
    new = old
    return string(new)

def generate_poisson_array(width: int, height: int) -> list:
    arr = np.random.poisson(5, width * height)
    return arr

def distribution(array: list) -> list:
    d = {}
    for x in array:
        if x not in d:
            d[x] = 1
        else:
            d[x] += 1
    return d

def replace_cell_with_stairs(
        matrix: list, 
        upstairs: tuple=None, 
        downstairs: tuple=None
    ) -> list:
    w, h = dimensions(matrix)
    if upstairs and downstairs and upstairs == downstairs:
        raise ValueError("Upstairs value cannot be the same as downstairs.")
    floors = [
        (x, y)
            for x in range(w) for y in range(h)
                if matrix[y][x] == '.'
    ]
    if len(floors) < 3:
        raise Exception("No room for both down and up stairs")
    random.shuffle(floors)
    if not upstairs:
        upstairs = floors.pop()
    matrix[upstairs[1]][upstairs[0]] = '<'
    if not downstairs:
        downstairs = floors.pop()
    matrix[downstairs[1]][downstairs[0]] = '>'
    return matrix

def array_to_matrix(
        array: list, 
        width: int, 
        height: int, 
        filterer: object,
        chars: tuple = ('#', '.')
    ) -> list:
    matrix = [[None for _ in range(width)] for _ in range(height)]
    for i in range(width):
        for j in range(height):
            if filterer(array[j * width + i]):
                matrix[j][i] = chars[0]
            else:
                matrix[j][i] = chars[1]
    return matrix

def add_boundry_to_matrix(matrix: list, bounds=2) -> list:
    width, height = dimensions(matrix)
    # vertical sides (left, right)
    x_points = []
    for x in range(bounds, 0, -1):
        x_points.append(bounds - x)
        x_points.append(width - x)
    for i in x_points:
        for j in range(height):
            matrix[j][i] = '#'
    # horizontal sides (top, bottom)
    y_points = []
    for y in range(bounds, 0, -1):
        y_points.append(bounds - y)
        y_points.append(height - y)
    for j in y_points:
        for i in range(width):
            matrix[j][i] = '#'
    return matrix

def add_blob(matrix: list) -> list:
    return matrix

def cell_auto(matrix: list, alivelimit: int=4, deadlimit: int=5) -> list:
    w, h = dimensions(matrix)
    copy = deepcopy(matrix)
    for i in range(w):
        for j in range(h):
            cell = matrix[j][i]
            neighbors = 0
            alive = 0
            for ii, jj in squares(exclude_center=True):
                # check if neighbor is within bounds
                try:
                    c = matrix[j+jj][i+ii]
                except:
                    pass
                else:
                    alive += 1
                    if c == '#':
                        neighbors += 1
            if alive < 6:
                continue
            if cell == '#':
                if neighbors < deadlimit:
                    copy[j][i] = '.'
            elif cell == '.':
                if neighbors > alivelimit:
                    copy[j][i] = '#'
    return copy

def flood_fill(matrix:list) -> list:
    w, h = dimensions(matrix)
    floors = {
        (x, y) 
            for x in range(w) for y in range(h)
                if matrix[y][x] == '.'
    }
    # dfs search
    groups = []
    while floors:
        group = []
        queue = [floors.pop()]
        while queue:
            x, y = queue.pop()
            group.append((x, y))
            # for i, j in squares(exclude_center=True):
            for i, j in ((-1, 0), (1, 0), (0, 1), (0, -1)):
                if (x + i, y + j) in floors:
                    floors.remove((x+i, y+j))
                    queue.append((x+i, y+j))
        groups.append(group)
    groups.sort(key=lambda x: len(x), reverse=True)
    for group in groups[1:]:
        for (x, y) in group:
            matrix[y][x] = '#'
    return matrix

def burrow_passage(width: int, height: int, matrix: list=None) -> list:
    if not matrix:
        matrix = [['#' for _ in range(width)] for _ in range(height)]
    else:
        width, height = dimensions(matrix)
    x = (width // 2) + random.randint(-width // 4, width // 4)
    length = width // 4 + random.randint(0, width // 8)
    for h in range(height):
        if x > width // 2:
            x = width - x
        for i in range(x, x + length):
            matrix[h][i] = '.'
        x = max(1, min(width - 1, x + random.randint(-1, 1)))
        length += random.randint(0, 1)
        length = max(3, min(width // 2, length))
    return matrix

weights = {
    (-1, 0): 37.5,
    (1, 0): 37.5,
    (0, -1): 12.5,
    (0, 1): 12.5
}
def drunkards_walk(width: int, height: int, limit=.45, m=None) -> list:
    if not m:
        m = empty_matrix(width, height, char='#')
    area = width * height
    cells = int(area * limit)
    tiles = { 
        (x, y) 
            for x in range(1, width-1)
                for y in range(1, height-1) 
    }
    dug = set()
    # x, y = random.randint(1, width-1), random.randint(1, height-1)
    x, y = width // 2, height // 2
    while True:
        dug.add((x, y))
        if len(dug) >= cells:
            break
        directions = []
        choices = []
        for a, b in cardinal(exclude_center=True):
            if (x+a, y+b) in tiles:
                directions.append((x + a, y + b))
                choices.append(weights[(a, b)])
        x, y = random.choices(directions, weights=choices).pop()
    for x, y in dug:
        m[y][x] = '.'
    return m

def lpath(b1, b2):
    x1, y1 = center(b1)
    x2, y2 = center(b2)

    # check if xs are on the same axis -- returns a vertical line
    if x1 == x2 or y1 == y2:
        return bresenhams((x1, y1), (x2, y2))

    # check if points are within x bounds of each other == returns the midpoint vertical line
    elif b2[0] <= x1 < b2[2] and b1[0] <= x2 < b1[2]:
        x = (x1+x2)//2
        return bresenhams((x, y1), (x, y2))

    # check if points are within y bounds of each other -- returns the midpoint horizontal line
    elif b2[1] <= y1 < b2[3] and b1[1] <= y2 < b2[3]:
        y = (y1+y2)//2
        return bresenhams((x1, y), (x2, y))
    else:
        # we check the slope value between two boxes to plan the path
        slope = abs((max(y1, y2) - min(y1, y2))/((max(x1, x2) - min(x1, x2)))) <= 1.0
    
        # low slope -- go horizontal
        if slope:
            # width is short enough - make else zpath
            return bresenhams((x1, y1), (x1, y2)) \
                + bresenhams((x1, y2), (x2, y2))

        # high slope -- go vertical
        else:
            return bresenhams((x1, y1), (x2, y1)) \
                + bresenhams((x2, y1), (x2, y2))

def bresenhams(start, end):
    """Bresenham's Line Algo -- returns list of tuples from start and end"""

    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points

def intersects(minx, miny, maxx, maxy, other):
    o = 0 # offset
    return (minx < other[2] + o and miny < other[3] + o and 
            maxx > other[0] - o and maxy > other[1] - o)

def center(room):
    return (room[0] + room[2]) // 2, (room[1] + room[3]) // 2

def distance(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    return math.sqrt(x**2 + y**2)

def maze(matrix: list):
    ...

def wall_coordinates(room):
    for y in (room[1], room[3]):
        for x in range(room[0], room[2]+1):
            yield x, y
    for x in (room[0], room[2]):
        for y in range(room[1]+1, room[3]):
            yield x, y

def add_maze(cave, rooms):
    """ `example`
        +-------------------------+
        |                         |
        | ##########              |
        | #........#    ######### |
        | #........#    #.......# |
        | #........#    #.......# |
        | ##########    #.......# |
        |               ######### |
        |                         |
        +-------------------------+
        1.start from corner
        +-------------------------+
        |             ############|
        | ##########  #           |
        | #........#  # ##########|
        | #........#  # #.......# |
        | #........#  # #.......# |
        | ##########  # #.......# |
        |    #   # #  # ######### |
        |###   #   #              |
        +-------------------------+
    """

def add_doors(cave, rooms):
    # create doors based on specific rules
    # _ | 0 1 2
    # --+-------
    # 0 | 0 1 2
    # 1 | 3 4 5
    # 2 | 6 7 8
    # if the tile @ 5 has neighbors only at 2/8 or 4/6 that are both walls
    # and the 5 tile is a floor then the 5 tile can transform into a door
    transform = set()
    width, height = dimensions(cave)
    for r, room in enumerate(rooms):
        # chance to a closed room
        if not random.randint(0, 1):
            continue
        # x, y = center(room)
        # cave[y][x] = r+1
        for x, y in wall_coordinates(room):
            if cave[y][x] != '.':
                continue
            subset = empty_matrix(3, 3, ' ')
            # check both cases to generate a door
            for i, j in squares(exclude_center=True):
                if x + i > width - 1:
                    continue
                if y + j > height - 1:
                    continue
                subset[j+1][i+1] = cave[y+j][x+i]
            added = 0
            # 1/7 are walls, 3/5 are floors
            if (subset[0][1] == '#' and 
                subset[2][1] == '#' and 
                (x - 1, y) not in transform and 
                (x + 1, y) not in transform
            ):
                transform.add((x, y))
                added = 1
            # 3/5 are walls, 1/7 are floors
            elif (subset[1][0] == '#' and
                subset[1][2] == '#' and 
                (x, y - 1) not in transform and
                (x, y + 1) not in transform
            ):
                transform.add((x, y))
                added = 2
            # print(string(subset), f'{r+1} {cave[y][x]} {added}\n')
    for x, y in transform:     
        cave[y][x] = '+'

def build_cave(width, height):
    cave = empty_matrix(width, height, ' ')
    tries = 0
    max_rooms = 12
    spaces = set()
    rooms = list()

    widths = {
        0: (6, 8),
        1: (9, 11),
        2: (12, 14)
    }

    # generation
    while len(rooms) < max_rooms and tries < 3000:
        room_size_key = random.choice(range(3))
        # w = random.randint(*widths[room_size_key])
        w = random.randint(8, width // 3)
        h = random.randint(5, max(5, w // 3 + 1))
        minx = random.randint(0, width - w - 1)
        miny = random.randint(0, height - h - 1)
        maxx = minx + w
        maxy = miny + h

        intersected = False
        for room in rooms:
            intersected = intersects(minx, miny, maxx, maxy, room)
            if intersected:
                break
        if not intersected:
            rooms.append((minx, miny, maxx, maxy))
        else:
            tries += 1

    graph = dict()
    for i, a in enumerate(rooms):
        distances = {}
        for j, b in enumerate(rooms):
            if i != j:
                distances[j] = distance(center(a), center(b))
        graph[i] = distances
    # save pairs before mst runs
    pairs = {
        (a, b)
            for a, bs in graph.items() 
                for b in bs
    }
    # create minimum spanning tree
    mst = create_mst(graph)
    pairs.difference_update({ 
        (a, b) 
            for a, b in mst.items() 
    })

    # bind some rooms with old links to add cycles
    number_of_links_rebuilt = int(len(pairs) * .15)
    pair_list = list(pairs)
    random.shuffle(pair_list)
    for i in range(number_of_links_rebuilt):
        x, y = pair_list.pop()
        val = mst[x]
        if isinstance(val, list):
            mst[x].append(y)
        else:
            mst[x] = [val, y]

    room_tiles = set()
    # post processing
    # add floor and wall tiles per room instance
    for i, room in enumerate(rooms):
        # add floor tiles
        for y in range(room[1]+1, room[3]):
            for x in range(room[0]+1, room[2]):
                cave[y][x] = '.'
                room_tiles.add((x, y))
        # add walls
        for x, y in wall_coordinates(room):
                cave[y][x] = '#'
        # make rooms circular
        # regular = random.randint(0, 2)
        # if not regular:
        #     cave[room[1]+1][room[0]+1] = '#'
        #     cave[room[1]+1][room[2]-1] = '#'
        #     cave[room[3]-1][room[2]-1] = '#'
        #     cave[room[3]-1][room[0]+1] = '#'

    # carve out paths using lpath
    # for i, (a, b) in enumerate(mst.items()):
    #     if isinstance(b, int):
    #         if a != b:
    #             for x, y in lpath(rooms[a], rooms[b]):
    #                 cave[y][x] = '.'
    #                 for i, j in squares(exclude_center=True):
    #                     if cave[y+j][x+i] == ' ':
    #                         cave[y+j][x+i] = '#'
    #     else:
    #         for c in b:
    #             for x, y in lpath(rooms[a], rooms[c]):
    #                 cave[y][x] = '.'
    #                 for i, j in squares(exclude_center=True):
    #                     if cave[y+j][x+i] == ' ':
    #                         cave[y+j][x+i] = '#'
    # -- or maze paths algo ---
    add_maze(cave, rooms)

    # doors added to map
    add_doors(cave, rooms)

    # add some stairs
    room_tiles = list(room_tiles)
    random.shuffle(room_tiles)
    x, y = room_tiles.pop()
    cave[y][x] = '<'
    x, y = room_tiles.pop()
    cave[y][x] = '>'
    return cave

def build_blob(width, height):
    cave = empty_matrix(width, height, ' ')
    # make a random blob
    ...
    return cave
