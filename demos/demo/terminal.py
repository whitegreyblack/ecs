# terminal.py

# Wrapper for curses screen
import curses

class Terminal:
    def __init__(self, screen):
        self.screen = screen
        self.height, self.width = screen.getmaxyx()

    def border(self, title):
        self.screen.border()
        self.add_string(1, 0, f"[{title}]")

    def add_char(self, x, y, char, color=0):
        self.screen.addch(y, x, char, color)
    
    def add_string(self, x, y, string, color=0):
        self.screen.addstr(y, x, string, color)

    def getch(self):
        return self.screen.getch()

    def erase(self):
        self.screen.erase()

    def refresh(self):
        self.screen.refresh()

    def flush_input(self):
        curses.flushinp()
