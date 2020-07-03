# keyboard_capture

"""Returns number code for any given keyboard input used in curses terminal"""

import curses

def main(screen):
    print(screen.getch())

if __name__ == "__main__":
    curses.wrapper(main)

