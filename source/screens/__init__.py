# source.screens.__init__.py

from .death_screen import DeathScreen
from .equipment_screen import EquipmentScreen
from .game_screen import GameScreen
from .inventory_screen import InventoryScreen
from .menu_screen import MenuScreen
from .screen import Screen
from .spell_screen import SpellScreen
from .start_screen import StartScreen

__all__ = [
    screen.__name__ 
        for screen in Screen.__subclasses__()
]
