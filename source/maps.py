# maps.py

"""Holds default maps and map functions used for testing"""

import random
from .common import squares


def create_field_matrix(width: int, height: int, char: chr='"') -> list:
    matrix = [['.' for _ in range(width)] for _ in range(height)]
    limit = int(.30 * (width * height))
    stack = []
    pool = [ (x, y) for x in range(width) for y in range(height) ]
    random.shuffle(pool)
    grown = set()
    while True:
        probability = 3
        x, y = pool.pop(0)
        stack.append((x, y, probability))
        while stack:
            x, y, p = stack.pop(0)
            grown.add((x, y))
            if p == 0:
                continue
            for xx, yy in squares(exclude_center=True):
                nx, ny = x + xx, y + yy
                if not (0 <= nx < width and 0 <= ny < height):
                    continue
                if (nx, ny) in grown or (nx, ny) not in pool:
                    continue
                chance = random.randint(0, p)
                if chance > 0:
                    pool.remove((nx, ny))
                    stack.append((nx, ny, p-1))
        if len(grown) >= limit or not pool:
            break
    for (x, y) in grown:
        matrix[y][x] = char
    return matrix

def create_empty_matrix(width: int, height: int, char: chr='.') -> list:
    matrix = []
    for h in range(height):
        matrix.append(list(char * width))
    return matrix

def create_empty_string(width: int, height: int, char: chr='.') -> str:
    matrix = []
    for h in range(height):
        matrix.append('.' * width)
    return '\n'.join(matrix)

# example rooms
def create_empty_room(width: int, height: int) -> str:
    room = []
    for h in range(height):
        if h in (0, height - 1):
            row = '#' * width
        else:
            row = '#' + '.' * (width - 2) + '#'
        room.append(row)
    return '\n'.join(room)

def rotate(mapstring):
    arr = [list(row) for row in mapstring.split('\n')]
    width = len(arr[0])
    height = len(arr)
    rows = []
    for y in range(width):
        rows.append(''.join(arr[height-x-1][y] for x in range(height)))
    return '\n'.join(rows)

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

def matrixfy_string(string):
    return [list(row) for row in string.split('\n')]

def stringify_matrix(matrix):
    return '\n'.join(''.join(row) for row in matrix)

def extend(mapstring, mapgen=create_empty_matrix, char='"'):
    old = matrixfy_string(mapstring)
    # w, h = max(len(old[0]), 58), max(len(old), 19)
    new = mapgen(60, 17, char)
    new = center_mapstring(old, new)
    new = old
    return stringify_matrix(new)

HALL = create_empty_room(100, 50)

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
..........##+##..##+##..##+##..#####.#####....#........#..
.#######.""....................#...#.....#....#.#....#.#..
.#.....#..""...................#...+.....#....#........#..
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

def to_array(mapstring):
    return [[int(c not in ('.', '/')) for c in row] for row in mapstring.split('\n')]

if __name__ == "__main__":
    print(dungeon.keys())
