# keyboard.py

"""
Keyboard object that maps ascii values to a string value
"""

# A-Za-z
# starts with 'A' and 'a' then iterates 26 characters
keyboard = { 
    i: chr(i) for x in (65, 97) for i in range(x, x + 26) 
}

# arrow keys and other characters
keyboard.update({
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
    126: 'tilde'
})

movement_keypresses = (
    'up-left', 'up', 'up-right', 'left', 'center', 'right', 'down-left', 
    'down', 'down-right',
)

movement_charpresses = (
    258, 259, 260, 261, 449, 450, 451, 452, 454, 455, 456, 457
)

keypress_to_direction = {
    'down': ( 0,  1),
    'down-left': (-1, 1),
    'down-right': (1, 1),
    'up': ( 0, -1),
    'up-left': (-1, -1),
    'up-right': (1, -1),
    'left': (-1,  0),
    'right': ( 1,  0),
    'center': (0, 0)
}

menu_keypresses = {
    'escape', 
    'enter', 
    'down', 
    'up'
}