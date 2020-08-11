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
    for u in units?:
        initative (was turn)
        energy (was turn)
        if ai:
            ai
        else:
            input
        move (was command)
        attack (was command)
        other
        grave
    decay
    heal
    mana
    spawn

new game flow - 8/11
divided into per turn vs per turn(s)
pre-turn systems ->
    | ... (statuses? heal?)

turn system ->
    | for i, position in e.positions:
    |     if position.moves == true:
    |       e.add(i, action)
action system ->
    | for i, _ in e.actions:

post-turn systems ->
    | ... (also statuses? burn?)
ex:
  lava corridor
    g : speed = 3
    a : speed = 2
  # # # # # # #
  # g . . . @ #
  # # # # # # #
    heal_system -> post-turn that recovers health before action phase
    turn_system -> determines who can move (adds action component)? energy?
    initiative_system -> determines who goes first (adds turn order based on speed)
    action_system -> take action -> move | attack
    burn_system -> status effect due to environment
    death_system -> if hp falls below 1, remove entity
    player_alive_system? -> check for player death after each turn
        | if e.player.health < 1:
        |     e.scene = player_death_screen
"""
