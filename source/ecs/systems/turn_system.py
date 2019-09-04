# turn_system.py

from .system import System


class TurnSystem(System):
    def process(self):
        while True:
            entity = self.engine.entity
            # end of entity list
            if entity is None:
                self.engine.reset_entity_index()
                break
            takes_turn = self.engine.inputs.find(entity)
            # skip entities that do not take a turn
            if not takes_turn:
                self.engine.next_entity()
                continue
            # if entity needs input from user then return early indicating input
            if takes_turn.needs_input:
                if self.engine.requires_input:
                    return False
                command = self.engine.get_keypress()
                self.engine.requires_input = True
            else:
                command = self.engine.ai_system.process(entity)
            turn_over = self.engine.command_system.process(entity, command)
            if takes_turn.needs_input:
                if not turn_over:
                    return True
                else:
                    self.engine.ai_system.update()
            if not self.engine.player:
                self.engine.change_screen('deathmenu')
                return True
            self.engine.grave_system.process()
            self.engine.next_entity()
        # end of turn stuff here
        self.engine.decay_system.process()
        self.engine.heal_system.process()
        self.engine.manaregen_system.process()
        self.engine.spawn_system.process()
        return True
