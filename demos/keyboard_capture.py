# keyboard_capture

import curses

def main(screen):
    print(screen.getch())


if __name__ == "__main__":
    curses.wrapper(main)