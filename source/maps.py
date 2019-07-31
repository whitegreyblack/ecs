# maps.py

"""Holds default maps and map functions used for testing"""

import random
from copy import deepcopy

import numpy as np

from .common import squares


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

def dimensions(matrix):
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
            if h in (0, height - 1) else ('#' + '.' * (width - 2) + '#')
                for h in range(height)
    ]

def rotate_string(mapstring):
    '''string -> matrix -> rotate() -> matrix -> string'''
    return string(rotate(matrix(mapstring)))

def rotate(matrix):
    width, height = dimensions(matrix)
    arr = empty_matrix(height, width)
    # print('matrix')
    # print(string(matrix))
    # print('arr')
    # print(string(arr))
    for y in range(height):
        for x in range(width):
            try:
                c = matrix[y][x]
            except:
                print(width, height, dimensions(arr))
                raise Exception("outer", x, y)
            else:
                try:
                    arr[x][y] = c
                except:
                    raise Exception("inner", x, y)
    # print('matrix')
    # print(string(matrix))
    # print('arr')
    # print(string(arr))
    return arr # [
    #     ''.join(arr[height-x-1][y] for x in range(height)) 
    #         for y in range(width)
    # ]

def center_mapstring(old: list, new: list):
    new_width, new_height = len(new[0]), len(new)
    old_width, old_height = len(old[0]), len(old)

    # if new_width == old_width and new_height == old_height:
    #     return old

    xoffset = (new_width - old_width) // 2
    yoffset = (new_height - old_height) // 2

    for y in range(old_height):
        for x in range(old_width):
            if old[y][x] == '.':
                continue
            new[y+yoffset][x+xoffset] = old[y][x]
    return new

def extend(mapstring, mapgen=empty_matrix, char='"'):
    old = matrix(mapstring)
    # w, h = max(len(old[0]), 58), max(len(old), 19)
    new = mapgen(60, 17, char)
    new = center_mapstring(old, new)
    new = old
    return string(new)

def generate_poisson_array(width: int, height: int):
    return np.random.poisson(5, width * height)

def replace_cell_with_stairs(
        matrix: list, 
        upstairs: tuple=None, 
        downstairs: tuple=None
    ):
    w, h = dimensions(matrix)
    if upstairs and downstairs and upstairs == downstairs:
        raise ValueError("Upstairs value cannot be the same as downstairs.")
    floors = [
        (x, y)
            for x in range(w) for y in range(h)
                if matrix[y][x] == '.'
    ]
    random.shuffle(floors)
    if not upstairs:
        while True:
            x, y = floors.pop()
            for i, j in squares(exclude_center=True):
                if (x+i, y+j) not in floors:
                    x, y = None, None
                    break
            if x and y:
                upstairs = (x, y)
                break
    matrix[upstairs[1]][upstairs[0]] = '<'
    while not downstairs:
        while True:
            x, y = floors.pop()
            for i, j in squares(exclude_center=True):
                if (x+i, y+j) not in floors:
                    x, y = None, None
                    break
            if x and y:
                downstairs = (x, y)
                break
    matrix[downstairs[1]][downstairs[0]] = '>'
    return matrix

def transform_random_array_to_matrix(array, width, height, filterpoint):
    matrix = [[None for _ in range(width)] for _ in range(height)]
    for i in range(width):
        for j in range(height):
            if array[j * width + i] == filterpoint:
                matrix[j][i] = '#'
            else:
                matrix[j][i] = '.'
    return matrix

def add_boundry_to_matrix(matrix):
    width, height = dimensions(matrix)
    for i in (0, 1, width-2, width-1):
        for j in range(height):
            matrix[j][i] = '#'
    for j in (0, 1, height-2, height-1):
        for i in range(width):
            matrix[j][i] = '#'
    return matrix

def cell_auto(matrix, alivelimit=4, deadlimit=5):
    copy = deepcopy(matrix)
    w, h = dimensions(matrix)
    for i in range(w):
        for j in range(h):
            cell = matrix[j][i]
            neighbors = 0
            for ii in range(-1, 2):
                for jj in range(-1, 2):
                    # check if neighbor is within bounds
                    try:
                        c = matrix[j+jj][i+ii]
                    except:
                        pass
                    else:
                        if c == '#':
                            neighbors += 1
            if cell == '#':
                if neighbors < deadlimit:
                    copy[j][i] = '.'
            elif cell == '.':
                if neighbors > alivelimit:
                    copy[j][i] = '#'
    return copy

def flood_fill(matrix):
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
            for i, j in squares(exclude_center=True):
                if (x + i, y + j) in floors:
                    floors.remove((x+i, y+j))
                    queue.append((x+i, y+j))
        groups.append(group)
    groups.sort(key=lambda x: len(x), reverse=True)
    for group in groups[1:]:
        for (x, y) in group:
            matrix[y][x] = '#'
    return matrix

def burrow_passage(height:int, width:int, matrix:list=None) -> list:
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

CHOKE = string(rotate(burrow_passage(60, 17)))

HALL = empty_room(100, 50)

DUNGEON = """
###########################################################
#....#....#....#....#..........##....#....#....#....#.....#
#...................#..........##...................#.....#
#....#....#....#..........#....##....#....#....#....#.....#
#.........................................................#
#....#....#....#....#................#....#....#....#.....#
#....#....#....#....#..........##....#....#....#....#.....#
#.........................................................#
#....#....#....#..........#....##....#....#....#....#.....#
#.........................................................#
#.........................................................#
#....#....#....#....#................#....#....#....#.....#
#....#....#....#....#..........##....#....#....#....#.....#
#.........................................................#
#.........................................................#
#.........................................................#
###########################################################"""[1:]

SHADOWBARROW = """
..........................................................
..........#####..#####..#####..###########.......####.....
..........#...#..#...#..#...#..#...#.#...#......##..##....
..........#...#..#...#..#...#..#...+.+...#....###....###..
..........##+##..##+##..##+##..#####.#####....#....>...#..
.#######.""..".................#...#.....#....#.#....#.#..
.#.....#.."";".................#...+.....#....#........#..
.#.....#.""."..................#####+#####....#........#..
.#.....#.....................................##.#....#.##.
.#.....+.....................................+..........#.
.#.....#.....................................##........##.
.#.....#.......................###+######....#..#....#..#.
.#######..##+##..##+##..##+##..#........#....#..........#.
..........#...#..#...#..#...#..#........#....###......###.
..........#...#..#...#..#...#..#........#......##....##...
..........#####..#####..#####..##########.......######....
.........................................................."""[1:]

RUINED = """
..........................................................
..........#####..####...#..##..###..###.##.......####.....
..........#....................#.....#..........##..##....
..............#......#..#...#..#.........#....###....###..
.............##..#..##..##......###...#..#....#....>...#..
.##..###."".."...........................#....#.#....#.#..
.#........"";".................##.............#........#..
.#.....#.""."..................#..##...#......#........#..
.......#.....................................##.#....#.##.
.............................................+..........#.
.......#.....................................##........##.
.#.............................###+######....#..#....#..#.
.#.###.......#...#......##+##..#........#....#..........#.
..............#......#..#...#..#........#....###......###.
..........#..........#..#...#..#........#......##....##...
..........##.##..##..#..#####..##########.......######....
.........................................................."""[1:]

ROGUE = """
###################################################
##################.........########################
###############......................##############
###############.##.........#########.##############
#.....#########.##.........####..................##
#...............##.........####..................##
#.....#########.##.........####..................##
###########.....###.......#####..................##
###########.########.....######..................##
###..........####################.#################
###..........#################......###############
###..........#################......###############
###################################################"""[1:]

BASIN = """
##########################
#......###################
#......###########.......#
#......+.........+.......#
#......#####'#####.......#
####+#######.#######+#####
##....######+#####.....###
##....######.+.........###
##....############.....###
##########################"""[1:]

PARENT = """
#############
#..........##
#.<......>..#
#..........##
#############"""[1:]

CHILD = """
######
#....#
#..<.#
#....#
######"""[1:]

# string maps added to config are pulled from variables() and added to list
dungeons = {
    k.lower(): v for k, v in vars().items()
        if not k.startswith('__') and isinstance(v, str)
}

if __name__ == "__main__":
    print('DUNGEONS:')
    print(' -', '\n - '.join(dungeons.keys()))
