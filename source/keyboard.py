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
}) 
