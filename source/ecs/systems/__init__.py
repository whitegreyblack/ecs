from .ai_system import AISystem
from .command_system import CommandSystem
from .decay_system import DecaySystem
from .energy_system import EnergySystem
from .grave_system import GraveSystem
from .input_system import InputSystem
from .render_system import RenderSystem
from .system import System
from .turn_system import TurnSystem

systems = System.__subclasses__()
