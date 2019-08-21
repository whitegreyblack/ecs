# maps.py

"""Holds default maps and map functions used for testing"""

import random
from copy import deepcopy

import numpy as np

from .common import squares, cardinal


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
    # print(arr, distribution(arr))
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

def l_path(start, end):
    x1, y1 = start
    x2, y2 = end
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1

    # calculate slope
    # dx = y2 - y1

    # determine which axis is longer
    # x_major = x2 - x1 > y2 - y1
    # if x_major:
    #     for x in range(x1, x2+1):
    #         yield x, y1
    #     for y in range(y1, y2+1):
    #         yield x, y
    # # else:
    for y in range(y1, y2+1):
        yield x1, y
    for x in range(x1, x2+1):
        yield x, y

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

CHOKE = string(rotate(burrow_passage(60, 17)))

STRESS = string(empty_room(500, 100))
HALL = string(empty_room(200, 80))
EMPTY = string(empty_room(58, 17))

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

SHADOWBARROW = '''
..........................................................
..........#####..#####..#####..###########.......####.....
..........#...#..#...#..#...#..#...#.#...#......##..##....
..........#...#..#...#..#...#..#...+.+...#....###....###..
..........##+##..##+##..##+##..#####.#####....#....>...#..
.#######.......................#...#.....#....#.#....#.#..
.#.....#.......................#...+.....#....#........#..
.#.....#.......................#####+#####....#........#..
.#.....#.....................................##.#....#.##.
.#.....+.....................................+..........#.
.#.....#.....................................##........##.
.#.....#.......................###+######....#..#....#..#.
.#######..##+##..##+##..##+##..#........#....#..........#.
..........#...#..#...#..#...#..#........#....###......###.
..........#...#..#...#..#...#..#........#......##....##...
..........#####..#####..#####..##########.......######....
..........................................................'''[1:]

COPY = '''
..........................................................
..........#####..#####..#####..###########.......####.....
..........#...#..#...#..#...#..#...#.#...#......##..##....
..........#...#..#...#..#...#..#...+.+...#....###....###..
..........##+##..##+##..##+##..#####.#####....#....>...#..
.#######.""..".................#...#.....#....#.#....#.#..
.#.....#.."""".................#...+.....#....#........#..
.#.....#.""."..................#####+#####....#........#..
.#.....#.....................................##.#....#.##.
.#.....+.....................................+..........#.
.#.....#.....................................##........##.
.#.....#.......................###+######....#..#....#..#.
.#######..##+##..##+##..##+##..#........#....#..........#.
..........#...#..#...#..#...#..#........#....###......###.
..........#...#..#...#..#...#..#........#......##....##...
..........#####..#####..#####..##########.......######....
..........................................................'''[1:]

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

ASTAR = string(empty_room(190, 44))

# string maps added to config are pulled from variables() and added to list
dungeons = {
    k.lower(): v for k, v in vars().items()
        if not k.startswith('__') and isinstance(v, str)
}

if __name__ == "__main__":
    print('DUNGEONS:')
    print(' -', '\n - '.join(dungeons.keys()))
