# keyboard.py

"""
Keyboard object that maps ascii values to a string value
"""

# A-Za-z
keyboard = { i: chr(i) for x in (65, 97) for i in range(x, x + 26) }
keyboard.update({
    258: 'down',
    259: 'up',
    260: 'left',
    261: 'right',
    27: 'escape',
    44: 'comma',

    # fn keypad
})

keyboard.update({
    449: 'up-left',
    450: 'up',
    451: 'up-right',
    452: 'left',
    453: 'center',
    454: 'right',
    455: 'down-left',
    456: 'down',
    457: 'down-right'
})

movement_keypresses = (
    258, 259, 260, 261, 449, 450, 451, 452, 454, 455, 456, 457
)