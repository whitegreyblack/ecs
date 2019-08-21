import curses

def main(stdscr):
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS-1):
        curses.init_pair(i + 1, i, -1)
    try:
        k = 8
        for j in range(100):
            for i in range(0, k):
                index = j * k + i
                if index > 255:
                    break
                stdscr.addstr(j, i * 4, str(index) + ' ', curses.color_pair(index))
    except:
        # End of screen reached
        pass
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
