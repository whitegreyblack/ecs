# astar.py

"""Sample demo to test astar implementation"""


import curses
import time
from dataclasses import dataclass

import click

from source.ecs.components import Position
from source.keyboard import keyboard
from source.maps import dimensions, dungeons, matrix
from source.pathfind import astar, bresenhams, cardinal

d = {
    (-1, -1): '7',
    (0, -1): '8',
    (1, -1): '9',
    (-1, 0): '4',
    (0, 0): '5',
    (1, 0): '6',
    (-1, 1): '1',
    (0, 1): '2',
    (1, 1): '3',
}
def direction(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    return d.get((x, y))

def main(screen, mapstring, finder):
    # setup colors
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)

    # setup mapf
    dungeon = matrix(mapstring)
    w, height = dimensions(dungeon)
    cursor = Position(w // 2, height // 2)
    blocked = ('#', '+')
    tiles = {
        (i, j)
            for j, row in enumerate(dungeon) 
                for i, cell in enumerate(row)
                    if cell not in blocked
    }
    a = None
    b = None
    changed = False
    path = None
    x_ruler = ''.join(str(i % 10) for i in range(w))

    while True:
        screen.erase()
        screen.addstr(0, 0, mapstring)
        # add width ruler
        for x in (0, w+1):
            screen.addstr(0, x, x_ruler)
        # add height ruler
        for j in range(len(dungeon)):
            screen.addch(j, 0, str(j % 10))
        if a:
            screen.addstr(a.y, a.x, 'a')
            screen.addstr(height+1, 0, f"a: {a.x:02}, {a.y:02}")
        if b:
            screen.addstr(b.y, b.x, 'b')
            screen.addstr(height+2, 0, f"b: {b.x:02}, {b.y:02}")
        if a and b and changed:
            start = time.time()
            if finder == "astar":
                path = astar(tiles, a, b, paths=cardinal)
            else:
                path = bresenhams(tiles, a, b)
            screen.addstr(height+6, 0, f"{time.time()-start}")
            changed = False
        if path:
            nheight = 0
            for x, y in path:
                screen.addch(y, x, 'o', curses.color_pair(3)) 
        screen.addstr(height, 0, f"c: {cursor.x:02}, {cursor.y:02}")
        screen.move(cursor.y, cursor.x)
        screen.refresh()
        char = screen.getch()
        keypress = keyboard[char]
        if keypress == 'q' or keypress == 'escape':
            break
        if keypress == 'up':
            cursor.y -= 1 if cursor.y > 1 else 0
        elif keypress == 'down':
            cursor.y += 1 if cursor.y < len(dungeon) - 1 else 0
        elif keypress == 'left':
            cursor.x -= 1 if cursor.x > 1 else 0
        elif keypress == 'right':
            cursor.x += 1 if cursor.x < len(dungeon[0]) - 1 else 0
        elif keypress == 'a':
            if not a or (a and a != cursor):
                a = Position(cursor.x, cursor.y)
                changed = True
            elif a and a == cursor:
                a = None
        elif keypress == 'b':
            if not b or (b and b != cursor):
                b = Position(cursor.x, cursor.y)
                changed = True
            elif b and b == cursor:
                b = None
        elif keypress == 'c':
            a = None
            b = None
            changed = False
            path = None

@click.command()
@click.option('-d', "--dungeon", default="shadowbarrow")
@click.option('-f', "--finder", default="astar")
def preload(dungeon, finder):
    m = dungeons[dungeon]
    curses.wrapper(main, m, finder)

if __name__ == "__main__":
    preload()
