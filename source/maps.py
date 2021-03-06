# maps.py

"""Holds premade levels used for testing"""

import enum

from source.generate import (burrow_passage, cell_auto, empty_room, rotate,
                             string)

class MapType:
    TOWN = 'town'
    CAVE = 'cave'

# generated levels
ASTAR = string(empty_room(190, 44))
CHOKE = string(cell_auto(rotate(burrow_passage(24, 50))))
EMPTY = string(empty_room(58, 17))
HALL = string(empty_room(200, 80))
STRESS = string(empty_room(500, 100))

m, n = 100, 80
LARGE = '\n'.join([
    ''.join('#' for x in range(m))
        if j == 0 or j == n-1 else
            '#' + ''.join('.' for x in range(m-2)) + '#'
                for j in range(n)
])

# handmade levels
DUNGEON = (MapType.CAVE, """
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
###########################################################"""[1:])

SHADOWBARROW = (MapType.TOWN, """
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
.........................................................."""[1:])

RUINED = (MapType.TOWN, """
..........................................................
..........#####..####...#..##..###..###.##.......####.....
..........#....................#.....#..........##..##....
..............#......#..#...#..#.........#....###....###..
.............##..#..##..##......###...#..#....#....>...#..
.##..###.................................#....#.#....#.#..
.#.............................##.............#........#..
.#.....#.......................#..##...#......#........#..
.......#.....................................##.#....#.##.
.............................................+..........#.
.......#.....................................##........##.
.#.............................###+######....#..#....#..#.
.#.###.......#...#......##+##..#........#....#..........#.
..............#......#..#...#..#........#....###......###.
..........#..........#..#...#..#........#......##....##...
..........##.##..##..#..#####..##########.......######....
.........................................................."""[1:])

ROGUE = (MapType.CAVE, """
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
###################################################"""[1:])

BASIN = (MapType.CAVE, """
##########################
#......###################
#......###########.......#
#......+.........+.......#
#......#####'#####.......#
####+#######.#######+#####
##....######+#####.....###
##....######.+.........###
##....############.....###
##########################"""[1:])

PARENT = (MapType.CAVE, """
#############
#....^^....##
#.<......>..#
#..........##
#############"""[1:])

CHILD = (MapType.CAVE, """
######
#....#
#..<.#
#....#
######"""[1:])

# string maps added to config are pulled from variables() and added to list
dungeons = {
    k.lower(): v for k, v in vars().items()
        if not k.startswith('__') and isinstance(v, tuple)
}

if __name__ == "__main__":
    print('DUNGEONS:')
    print(' -', '\n - '.join(dungeons.keys()))
