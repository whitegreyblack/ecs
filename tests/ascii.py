import curses

def main(screen):
    l = 6
    i, j = 0, 0
    h, w = screen.getmaxyx()
    for c in range(1, 2000):
        screen.addstr(j, l * i, f"{c} {chr(c)}")
        i += 1
        if w - l * i < l:
            j += 1
            i = 0
    screen.getch()

if __name__ == "__main__":
    curses.wrapper(main)