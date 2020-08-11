# keyboard.py

"""
Keyboard object that maps ascii values to a string value
"""

from bearlibterminal import terminal


# A-Za-z
# starts with 'A' and 'a' then iterates 26 characters
curses_keyboard = { 
    i: chr(i) for x in (65, 97) for i in range(x, x + 26)
}

# numeric characters
curses_keyboard.update({
    i + 48: str(i) for i in range(10)
})

# arrow keys and other characters
curses_keyboard.update({
    3: '^C',
    258: 'down',
    259: 'up',
    260: 'left',
    261: 'right',
    27: 'escape',
    44: 'comma',
    60: 'less-than',
    62: 'greater-than',
    10: 'enter',
    # fn keypad
    449: 'up-left',
    450: 'up',
    451: 'up-right',
    452: 'left',
    453: 'center',
    454: 'right',
    455: 'down-left',
    456: 'down',
    457: 'down-right',
    # debug key
    126: 'tilde',
    96: 'backtick',
})

movement_keypresses = (
    'up-left', 'up', 'up-right', 'left', 'center', 'right', 'down-left',
    'down', 'down-right',
)

movement_charpresses = (
    258, 259, 260, 261, 449, 450, 451, 452, 454, 455, 456, 457
)

keypress_to_direction = {
    'down': ( 0, 1),
    'down-left': (-1, 1),
    'down-right': (1, 1),
    'up': ( 0, -1),
    'up-left': (-1, -1),
    'up-right': (1, -1),
    'left': (-1, 0),
    'right': ( 1, 0),
    'center': (0, 0)
}

menu_keypresses = {
    'escape',
    'enter',
    'down',
    'up',
    'quit'
}

# add from a-z. blt uses shift/ctrl/alt state instead of capital letters
blt_keyboard = {
    i - 93 : chr(i) for i in range(97, 97 + 26)
}

# add special characters
blt_keyboard.update({
    terminal.TK_ESCAPE: 'escape', 
    terminal.TK_ENTER: 'enter',
    terminal.TK_CLOSE: 'close',
    terminal.TK_UP: 'up',
    terminal.TK_DOWN: 'down',
    terminal.TK_LEFT: 'left',
    terminal.TK_RIGHT: 'right',
    terminal.TK_COMMA: ('comma', 'less-than'),
    terminal.TK_PERIOD: ('period', 'greater-than'),
    terminal.TK_SLASH: ('slash', 'question-mark'),
    terminal.TK_GRAVE: ('backtick', 'tilde'),
    terminal.TK_MOUSE_MOVE: 'mouse-move',
    terminal.TK_MOUSE_LEFT: 'mouse-left',
    terminal.TK_MOUSE_RIGHT: 'mouse-right',
    terminal.TK_KP_1: 'down-left',
    terminal.TK_KP_2: 'down',
    terminal.TK_KP_3: 'down-right',
    terminal.TK_KP_4: 'left',
    terminal.TK_KP_5: 'wait',
    terminal.TK_KP_6: 'right',
    terminal.TK_KP_7: 'up-left',
    terminal.TK_KP_8: 'up',
    terminal.TK_KP_9: 'up-right'
})
