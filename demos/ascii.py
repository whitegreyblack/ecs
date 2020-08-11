import curses

def main(screen):
    l = 6
    i, j = 0, 0
    h, w = screen.getmaxyx()
    for c in range(32, 1500):
        screen.insstr(j, l * i, f"{c} {chr(c)}")
        i += 1
        if w - l * i < l:
            j += 1
            i = 0
        if j == h:
            break
    screen.getch()

if __name__ == "__main__":
    curses.wrapper(main)
