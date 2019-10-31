from .ai_system import AISystem
from .command_system import CommandSystem
from .decay_system import DecaySystem
from .energy_system import EnergySystem
from .grave_system import GraveSystem
from .health_system import HealSystem
from .input_system import InputSystem
from .look_system import LookSystem
from .mana_system import ManaRegenSystem
from .map_system import MapSystem
from .move_system import MoveSystem
from .render_system import RenderSystem
from .spawn_system import SpawnSystem
from .spell_system import SpellSystem
from .system import System
from .turn_system import TurnSystem

systems = System.__subclasses__()

"""
current game flow:
    # per unit turn
    for u in units:
        turn
        ai if ai else input
        command
        grave
    # per turn (after all units finish)
    decay
    heal
    mana
    spawn
future game flow:
    # per unit turn
    for u in units:
        initative (was turn)
        energy (was turn)
        ai if ai else input
        move (was command)
        attack (was command)
        other
        grave
    decay
    heal
    mana
    spawn
"""
