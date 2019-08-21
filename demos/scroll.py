# scroll.py

from source.common import scroll
from source.maps import create_field_matrix

import curses


def main(screen):
    curses.curs_set(0)
    world = create_field_matrix(100, 50, '#')
    w, h = len(world[0]), len(world)
    px, py = 0, 0
    
    while True:
        camera_x = scroll(px, 80, w)
        camera_y = scroll(py, 25, h)
        for y in range(camera_y, camera_y + 25):
            for x in range(camera_x, camera_x + 80):
                c = world[y][x]
                try:
                    screen.addch(y - camera_y, x - camera_x, c)
                except:
                    screen.insch(y - camera_y, x - camera_x, c)

        try:
            screen.addch(py - camera_y, px - camera_x, '@')
        except:
            screen.insch(px - camera_y, py - camera_x, '@')
        
        screen.refresh()
        c = screen.getch()
        if c == ord('q') or c == 27:
            break
        elif c == curses.KEY_UP:
            py -= 1
        elif c == curses.KEY_DOWN:
            py += 1
        elif c == curses.KEY_LEFT:
            px -= 1
        elif c == curses.KEY_RIGHT:
            px += 1
        px = min(99, max(0, px))
        py = min(49, max(0, py))

if __name__ == "__main__":
    curses.wrapper(main)
