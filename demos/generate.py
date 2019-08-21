# test_generate.py

import random
from dataclasses import dataclass

from source.astar import astar, cardinal
from source.maps import (add_blob, add_boundry_to_matrix, array_to_matrix,
                         bresenhams, burrow_passage, cell_auto, dimensions,
                         distribution, drunkards_walk, empty_matrix,
                         flood_fill, generate_poisson_array, l_path, matrix,
                         generate_poisson_array, replace_cell_with_stairs, rotate,
                         string)


@dataclass
class Node:
    x: int
    y: int

def main():
    random_array = generate_poisson_array(58, 17)
    matrix = array_to_matrix(random_array, 58, 17, lambda x: 3 <= x < 5)
    # print('initial')
    # print(string(matrix))
    bounded = add_boundry_to_matrix(matrix, bounds=1)
    # print('bounded')
    # print(string(bounded))
    no_stairs = bounded
    for i in range(4):
        no_stairs = cell_auto(no_stairs, deadlimit=5+(i-5))
        # print(f'cell auto {i+1}')
        # print(string(no_stairs))
    no_stairs = flood_fill(no_stairs)
    dungeon = replace_cell_with_stairs(no_stairs)
    print('with stairs')
    print(string(dungeon))

def flood_fill_test():
    random_array = generate_poisson_array(58, 17)

    matrix = array_to_matrix(random_array, 58, 17, lambda x: x < 3 or x >= 8)
    bounded = add_boundry_to_matrix(matrix, bounds=1)
    no_stairs = bounded
    for i in range(4):
        no_stairs = cell_auto(no_stairs, deadlimit=5+(i-5))
    print('before floodfill')
    print(string(no_stairs))
    no_stairs = flood_fill(no_stairs)
    dungeon = replace_cell_with_stairs(no_stairs)
    print(string(dungeon))

def burrowing_algo_vertical():
    print(string(burrow_passage(58, 17)))

def burrowing_algo_horizontal():
    print(string(rotate(burrow_passage(58, 17))))

def double_map_join():
    w, h = 191, 50
    maps = [generate_poisson_array(w, h), generate_poisson_array(w, h)]
    for n in range(len(maps)):
        d = maps[n]
        d = array_to_matrix(d, w, h, lambda x: x < 4 or x >= 9)
        d = add_boundry_to_matrix(d, bounds=1)
        for i in range(5):
            d = cell_auto(d, deadlimit=5+(i-5))
        print(string(d))
        d = flood_fill(d)
        maps[n] = d
    for m in maps:
        print(string(m))
    m = [['.' if any(m[y][x] == '.' for m in maps) else '#' for x in range(w)] for y in range(h)]
    print(string(m))

def draw_paths_using_astar():
    paramaters = (
        ((4, 4), Node(1, 1), Node(2, 2)),
        ((4, 5), Node(1, 1), Node(2, 3)),
        ((5, 4), Node(1, 1), Node(3, 2)),
        ((6, 4), Node(1, 1), Node(4, 2)),
        ((40, 40), Node(35, 24), Node(1, 1)),
    )
    for box, start, end in paramaters:
        empty = empty_matrix(*box, '#')
        tiles = {
            (i, j)
                for j, row in enumerate(empty) 
                    for i, cell in enumerate(row)
        }
        for i, j in astar(tiles, start, end, paths=cardinal, include_start=True):
            empty[j][i] = '.'
        print(string(empty))

def draw_points(matrix: list, x0, y0, x1, y1, num=0):
    for y in (y0, y1):
        for x in (x0, x1):
            matrix[y][x] = str(num)

def partition_drunkards():
    w, h = 58, 17
    # map to be filled with smaller maps
    empty = empty_matrix(w, h)
    # box1
    x0, y0 = 0, 0
    xx0, yy0 = w//2, h//2
    # box 2
    x1, y1 = 0, h - yy0
    xx1, yy1 = w//2, yy0 + h//2
    # box 3
    x2, y2 = w - xx0 + 1, 0
    xx2, yy2 = xx0 + w//2-1, yy0 + h//2

    print(x0, y0, xx0, yy0)
    print(x1, y1, xx1, yy1)
    print(x2, y2 ,xx2, yy2)

    draw_points(empty, x0, y0, xx0, yy0, 1)
    draw_points(empty, x1, y1, xx1, yy1, 2)
    draw_points(empty, x2, y2, xx2, yy2, 3)

    print(string(empty))
    filterer = lambda x: x < 3 or x >= 8
    random_array = generate_poisson_array( xx0 - x0 + 1, yy0 - y0 + 1)
    m = array_to_matrix(random_array, xx0 - x0 + 1, yy0 - y0 + 1, filterer)
    print(string(cell_auto(add_boundry_to_matrix(m, bounds=1))))
    print(string(cell_auto(cell_auto(add_boundry_to_matrix(m, bounds=1)))))
    print(string(cell_auto(cell_auto(cell_auto(add_boundry_to_matrix(m, bounds=1))))))
    d0 = drunkards_walk(xx0 - x0 + 1, yy0 - y0 + 1, limit=.25, m=m)
    d1 = drunkards_walk(xx1 - x1 + 1, yy1 - y1 + 1, limit=.25)
    d2 = drunkards_walk(xx2 - x2 + 1, yy2 - y2 + 1, limit=.25)

    print(string(d0))
    print(string(d1))
    print(string(d2))
    
    x, y = dimensions(d0)
    d0_tiles = []
    for j in range(y):
        for i in range(x):
            c = d0[j][i]
            if c == '.':
                d0_tiles.append((i, j))
            empty[j][i] = c
    # print(string(empty))

    x, y = dimensions(d1)
    d1_tiles = []
    for j in range(y):
        for i in range(x):
            c = d1[j][i]
            if c == '.':
                d1_tiles.append((i, j))
            empty[j + y1][i + x1] = c
    # print(string(empty))

    x, y = dimensions(d2)
    d2_tiles = []
    for j in range(y):
        for i in range(x):
            c = d2[j][i]
            if c == '.':
                d2_tiles.append((i, j))
            empty[j + y2][i + x2] = c
    # print(string(empty))

    # connect them
    random.shuffle(d0_tiles)
    random.shuffle(d1_tiles)
    random.shuffle(d2_tiles)
    print(len(d0_tiles), len(d1_tiles), len(d2_tiles))
    print(d0_tiles[0], d0_tiles[-1])
    print(d1_tiles[0], d1_tiles[-1])
    print(d2_tiles[0], d2_tiles[-1])

    # set of tiles
    tiles = {
        (i, j)
            for j, row in enumerate(empty) 
                for i, cell in enumerate(row)
    }

    # connect 1 and 2 blobs
    a0, b0 = d0_tiles[0]
    i, j = d1_tiles[0]
    a1, b1 = i + x1, j + y1
    for i, j in astar(
        tiles, 
        Node(a0, b0), 
        Node(a1, b1), 
        paths=cardinal, 
        include_start=True
    ):
        if (i, j) == (a0, b0) or (i, j) == (a1, b1):
            empty[j][i] = 'X'
        else:
            empty[j][i] = '1'

    # connect 1 and 3 blobs
    a0, b0 = d0_tiles[-1]
    i, j = d2_tiles[0]
    a1, b1 = i + x2, j + y2

    for i, j in astar(
        tiles, 
        Node(a0, b0), 
        Node(a1, b1), 
        paths=cardinal, 
        include_start=True
    ):
        if (i, j) == (a0, b0) or (i, j) == (a1, b1):
            empty[j][i] = 'X'
        else:
            empty[j][i] = '2'

    # connect 2 and 3 blobs
    i, j = d1_tiles[-1]
    a0, a1 = i + x1, j + y1
    i, j = d2_tiles[-1]
    a1, b1 = i + x2, j + y2

    for i, j in astar(
        tiles, 
        Node(a0, b0), 
        Node(a1, b1), 
        paths=cardinal, 
        include_start=True
    ):
        if (i, j) == (a0, b0) or (i, j) == (a1, b1):
            empty[j][i] = 'X'
        else:
            empty[j][i] = '3'
    # print(a0, b0, a1, b1)
    print(string(empty))

    # connect 1 and 2 blobs
    a0, b0 = d0_tiles[0]
    i, j = d1_tiles[0]
    a1, b1 = i + x1, j + y1
    for i, j in astar(
        tiles, 
        Node(a0, b0), 
        Node(a1, b1), 
        paths=cardinal, 
        include_start=True
    ):
        empty[j][i] = '.'

    # connect 1 and 3 blobs
    a0, b0 = d0_tiles[-1]
    i, j = d2_tiles[0]
    a1, b1 = i + x2, j + y2

    for i, j in astar(
        tiles, 
        Node(a0, b0), 
        Node(a1, b1), 
        paths=cardinal, 
        include_start=True
    ):
        empty[j][i] = '.'

    # connect 2 and 3 blobs
    i, j = d1_tiles[-1]
    a0, a1 = i + x1, j + y1
    i, j = d2_tiles[-1]
    a1, b1 = i + x2, j + y2

    for i, j in astar(
        tiles, 
        Node(a0, b0), 
        Node(a1, b1), 
        paths=cardinal, 
        include_start=True
    ):
        empty[j][i] = '.'

    # print final map
    print(string(empty))

def test_lpath():
    # paramaters = (
    #     ((4, 4), Node(1, 1), Node(2, 2)),
    #     ((4, 5), Node(1, 1), Node(2, 3)),
    #     ((5, 4), Node(1, 1), Node(3, 2)),
    #     ((6, 4), Node(1, 1), Node(4, 2)),
    #     ((40, 40), Node(35, 24), Node(1, 1)),
    # )
    # for box, start, end in paramaters:
    #     empty = empty_matrix(*box, '#')
    #     for i, j in l_path(start, end)
    #         empty[j][i] = '.'
    #     print(string(empty))
    e = empty_matrix(60, 25)
    for i, j in l_path((0,0), (5, 10)):
        e[j][i] = '#'
    print(string(e))

if __name__ == "__main__":
    # main()
    # flood_fill_test()
    # burrowing_algo_vertical()
    # burrowing_algo_horizontal()
    # double_map_join()
    partition_drunkards()
    # test_lpath()
    # draw_paths_using_astar()
