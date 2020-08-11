# source.screens.__init__.py

from .confirm_menu_screen import ConfirmMenuScreen
from .death_screen import DeathScreen
from .empty_screen import EmptyScreen
from .equipment_screen import EquipmentScreen
from .game_menu_screen import GameMenuScreen
from .game_screen import GameScreen
from .inventory_screen import InventoryScreen
from .main_menu_screen import MainMenuScreen
from .screen import Screen
from .spell_screen import SpellScreen

__all__ = [ screen.__name__ for screen in Screen.__subclasses__() ]
